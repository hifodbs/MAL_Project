import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import os
import joblib
from inclLSTM import IncLSTMDual

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')


def prepare_dual_data(df, lookback=192, horizon=96):
    all_X_past, all_X_fut, all_y, all_t = [], [], [], []

    cols_past = ['AC_POWER', 'AMBIENT_TEMPERATURE', 'MODULE_TEMPERATURE', 'IRRADIATION', 'hour_sin', 'hour_cos']
    cols_fut = ['AMBIENT_TEMPERATURE', 'MODULE_TEMPERATURE', 'IRRADIATION', 'hour_sin', 'hour_cos']
    target = 'AC_POWER'

    scaler_past = MinMaxScaler()
    scaler_fut = MinMaxScaler()
    scaler_target = MinMaxScaler()

    data_past_scaled = scaler_past.fit_transform(df[cols_past])
    data_fut_scaled = scaler_fut.fit_transform(df[cols_fut])
    data_target_scaled = scaler_target.fit_transform(df[[target]])

    scalers = {
        'scaler_past': scaler_past,
        'scaler_fut': scaler_fut,
        'scaler_target': scaler_target
    }

    for inv in df['SOURCE_KEY'].unique():
        inv_mask = (df['SOURCE_KEY'] == inv)
        inv_idx = np.where(inv_mask)[0]

        d_p = data_past_scaled[inv_idx]
        d_f = data_fut_scaled[inv_idx]
        d_t = data_target_scaled[inv_idx]
        time_vals = df.iloc[inv_idx]['DATE_TIME'].values

        n_samples = len(d_p) - lookback - horizon + 1
        if n_samples > 0:
            idx_p = np.arange(n_samples)[:, None] + np.arange(lookback)[None, :]
            all_X_past.append(d_p[idx_p])

            idx_f = np.arange(n_samples)[:, None] + np.arange(lookback, lookback + horizon)[None, :]
            all_X_fut.append(d_f[idx_f])

            all_y.append(d_t[idx_f].squeeze())
            all_t.append(time_vals[np.arange(lookback, len(d_p) - horizon + 1)])

    if not all_X_past:
        raise ValueError("Not enough data to create windows.")

    X_past = np.concatenate(all_X_past)
    X_fut = np.concatenate(all_X_fut)
    y = np.concatenate(all_y)
    t = np.concatenate(all_t)

    sort_idx = np.argsort(t)

    return X_past[sort_idx], X_fut[sort_idx], y[sort_idx], t[sort_idx], scalers

print("Loading Data...")
df = pd.read_csv('cleaned_data/solar_1.csv')
df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'])
df['hour_sin'] = np.sin(2 * np.pi * df['DATE_TIME'].dt.hour / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['DATE_TIME'].dt.hour / 24)

LOOKBACK = 96 * 2
HORIZON = 96

print("Preparing Dual Inputs...")
X_all_p, X_all_f, y_all, t_all, scalers = prepare_dual_data(df, LOOKBACK, HORIZON)

scaler_filename = "solar_scalers.pkl"
joblib.dump(scalers, scaler_filename)
print(f"Scalers saved to {scaler_filename}")

last_timestamp = pd.to_datetime(t_all[-1])
cutoff_timestamp = last_timestamp - pd.Timedelta(hours=24)

print(f"Splitting data. Final Test Set starts after: {cutoff_timestamp}")

test_mask = t_all > cutoff_timestamp
working_mask = ~test_mask

X_test_p, X_test_f, y_test, t_test = X_all_p[test_mask], X_all_f[test_mask], y_all[test_mask], t_all[test_mask]
X_work_p, X_work_f, y_work, t_work = X_all_p[working_mask], X_all_f[working_mask], y_all[working_mask], t_all[working_mask]

print(f"Total Working Samples (Init + Stream): {len(y_work)}")
print(f"Final Held-out Test Samples: {len(y_test)}")

start_date = pd.to_datetime(t_work[0])
split_date = start_date + pd.Timedelta(days=7)
init_mask = t_work < split_date

X_p_init, X_f_init, y_init = X_work_p[init_mask], X_work_f[init_mask], y_work[init_mask]
X_p_stream, X_f_stream, y_stream, t_stream = X_work_p[~init_mask], X_work_f[~init_mask], y_work[~init_mask], t_work[~init_mask]



model = IncLSTMDual(LOOKBACK, 6, HORIZON, 3, buffer_size=5)

print(f"Cold Start Training ({len(y_init)} samples)...")
model.fit_incremental(X_p_init, X_f_init, y_init, epochs=20)

SEED = 2000
buf_X_p = list(X_p_init[-SEED:])
buf_X_f = list(X_f_init[-SEED:])
buf_y = list(y_init[-SEED:])
MAX_BUF = 3000

print("Starting Stream Loop...")

dates = pd.to_datetime(t_stream).date
unique_dates = np.unique(dates)

for current_date in unique_dates:
    idx = np.where(dates == current_date)[0]
    if len(idx) == 0: continue

    X_p_day = X_p_stream[idx]
    X_f_day = X_f_stream[idx]
    y_day = y_stream[idx]

    model.predict(X_p_day, X_f_day)

    model.update_weights_and_buffer(X_p_day, X_f_day, y_day)

    buf_X_p.extend(X_p_day)
    buf_X_f.extend(X_f_day)
    buf_y.extend(y_day)

    if len(buf_X_p) > MAX_BUF:
        buf_X_p = buf_X_p[-MAX_BUF:]
        buf_X_f = buf_X_f[-MAX_BUF:]
        buf_y = buf_y[-MAX_BUF:]

    model.fit_incremental(np.array(buf_X_p), np.array(buf_X_f), np.array(buf_y), epochs=15)
    print(f"Processed Day: {current_date}")

print("\nFINAL TEST ON HELD-OUT DATA (LAST 24 HOURS)")

pred_test_norm = model.predict(X_test_p, X_test_f)
pred_test_norm = np.maximum(pred_test_norm, 0)

t_scaler = scalers['scaler_target']
pred_test_real = t_scaler.inverse_transform(pred_test_norm)
y_test_real = t_scaler.inverse_transform(y_test)

mae_test = np.mean(np.abs(pred_test_real - y_test_real))
print(f"Final Test MAE (Last 24h): {mae_test:.2f} kW")

plt.figure(figsize=(12, 6))
plt.plot(y_test_real[-1], label='Actual (Held-out)', color='black', linewidth=2)
plt.plot(pred_test_real[-1], label='Predicted (Model)', color='lime', linestyle='--', linewidth=2)
plt.title(f"Final Test: Last 24h (MAE: {mae_test:.2f} kW)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()


print("\nSaving Final Model Ensemble...")
model_save_path = "final_solar_model"
model.save_system(model_save_path)

print(f"DONE")