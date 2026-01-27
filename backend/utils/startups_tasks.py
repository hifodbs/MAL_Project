from backend.utils.model_script import train_model_on_historical_data
from backend.dao.plant_dao import PlantsDAO
from datetime import datetime


def startup_tasks(app):

    print("Server strtup...")

    models = {}

    plants_dao = PlantsDAO("cleaned_data")
    plants = plants_dao.get_all()

    s ="2020-06-14 23:45:00"  # this is for simulation in the app
    end_time = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

    for plant in plants:
        print(f"\r\nInitialization of the model for plant {plant.name}")
        model, metric, adwin  = train_model_on_historical_data(
            data_directory="cleaned_data",
            plant_id=plant.id,
            end_time=end_time
        )
        models[plant.id] = (model, metric, adwin)
    
    print("\r\nModels initialization ended!\r\n")

    app.models = models