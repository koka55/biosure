from params import *
import time
import pickle
from glob import glob
from colorama import Fore, Style

def save_results(metrics):
    timestamp = time.strftime("%Y%m%d-%H%M%S")

    # Save metrics locally
    if metrics is not None:
        metrics_path = os.path.join(LOCAL_REGISTRY_PATH, "metrics", timestamp + ".pickle")
        with open(metrics_path, "wb") as file:
            pickle.dump(metrics, file)

    print("✅ Results saved locally")


def save_model(model):

    timestamp = time.strftime("%Y%m%d-%H%M%S")

    # Save model locally
    model_path = os.path.join(LOCAL_REGISTRY_PATH, "models", f"{timestamp}.h5")
    try:
        pickle.dump(model, model_path)
        print(f"✅ Model saved as {model_path}")
    except Exception as e:
        print(f"Error saving the model: {e}")

    return None



def load_model():

    if MODEL_TARGET == "local":
        print(Fore.BLUE + f"\nLoad latest model from local registry..." + Style.RESET_ALL)

        # Get the latest model version name by the timestamp on disk
        local_model_directory = os.path.join(LOCAL_REGISTRY_PATH, "models")
        local_model_paths = glob.glob(f"{local_model_directory}/*")

        if not local_model_paths:
            return None

        most_recent_model_path_on_disk = sorted(local_model_paths)[-1]

        try:
            loaded_model = pickle.load(most_recent_model_path_on_disk)
            print(f"Model loaded from {most_recent_model_path_on_disk}")
            return loaded_model
        except Exception as e:
            print(f"Error loading the model: {e}")
            return None
