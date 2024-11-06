# Seaing Clearly Project

## Setup

1. Please ensure pipx is installed before continuing

```bash
pip install pipx
```

2. Install poetry

```bash
pipx install poetry
```

3. Install project dependencies

```bash
poetry install
poetry shell
```

## Run Locally

Client

```bash
poetry run py-hot-reload seaingclearly/app.py
```

Server

```bash
poetry run py seaserver/app.py
```

# Documentation

## SeaServer

### 1. Authentication

Authentication to the SeaServer is handled by a code challenge.
To authenticate to the server the client or IOT device makes a POST request to the `/auth-challenge` endpoint with its device info in JSON format.
This JSON includes the `device_name`, `mac_address`, `ip_address`, `os_info`, `machine_info` & `uuid`.
The server verifes that the `uuid` recieved is legitimate by generating a SHA-1 hash (uuid5) of a portion of the device info using a predefined namespace. The result is then compared to the submitted `uuid` and a randomly generated code challenge is sent back.<br><br>
The client then makes a POST request to the `/authenticate` endpoint with its device info and completed code challenge (`challenge_code`).
Provided the challenge code has not expired (within 5 minutes), the server concatenates the challenge code with a secret (API_SECRET), hashes it using SHA-256, and compares the result with the modified code provided by the client.<br><br>
If the codes match, the session is marked as authenticated and the device info is saved to the system.

### Example

**POST** `/auth-challenge`<br>
**Request Body**

```json
{
  "device_info": {
    "device_name": "RASPBERRY-PIE-01",
    "mac_address": "00:d8:61:a9:cb:64",
    "ip_address": "192.168.1.10",
    "os_info": "Raspbian GNU/Linux 10 (buster)",
    "machine_info": "armv7l",
    "uuid": "ec1a91bb-7ff4-51c8-9c4c-90ff9d4f8af1"
  }
}
```

**200 Response**

```json
{
    {"challenge": "F44S3SCE5EKR6K3RRTJ7CBECJTWKFXIB"}
}
```

Client SHA-256 encodes challenge code with API_SECRET and sends the modified challenge code.

**POST** `/authenticate`<br>
**Request Body**

```json
{
  "device_info": {
    "device_name": "RASPBERRY-PIE-01",
    "mac_address": "00:d8:61:a9:cb:64",
    "ip_address": "192.168.1.10",
    "os_info": "Raspbian GNU/Linux 10 (buster)",
    "machine_info": "armv7l",
    "uuid": "ec1a91bb-7ff4-51c8-9c4c-90ff9d4f8af1"
  },
  "challenge_code": "aef8ebb66e846a02ac18777a59fa297c8bde95670dd1667b39b98402335747f0"
}
```

**200 Response**

```json
{
  "message": "Authentication Successful"
}
```

<br>

### 2. API Routes (protected by authentication checks)

- `/options` (GET)<br>
  This endpoint provides the client with available image enhancement options allowing setup configuration to be completely done server-side. It retrieves available enhancement options from the server and returns them in JSON format.

    **200 Response** 
    ```json
    {
        "enhancements": [
            {
                "name": "white_balance",
                "lbl": "White Balance Correction",
                "tt": "Applies white balance correction to enhance the color balance in the image."
            },
            {
                "name": "super_res_upscale",
                "lbl": "Super-Resolution Upscaling",
                "tt": "Enhances image resolution using super-resolution techniques. Is computationally expensive."
            },
            ...
        ]
    }
    ```
    <br>

- `/config` (POST)<br>
  This endpoint allows the client to set a configuration for image enhancement. The client submits a configuration object in JSON format, which is saved to the session. Note that the configuration keys are mapped by the names of the enhancements given from the `/options` endpoint. A success message is returned once the configuration is stored.

    **Request Body**
    ```json
    {
        "config": {
            "adaptive_histograph_equalisation": true,
            "richard_lucy_deconvolution": true,
            "super_res_upscale": true,
            "white_balance": true
        }
    }
    ```

    **200 Response**
    ```json
    { "message": "Configuration set" }
    ```
    <br>

- `/image/enhance` (POST)<br>
    This endpoint processes an uploaded image using the enhancement configuration stored in the session. The processed (enhanced) image is returned as a binary file. 

- `/logout` (POST)<br>
    This endpoint logs the user out by clearing the session.

    **200 Response**
    ```json
    {"message": "Logged out successfully"}
    ```
    <br>


### 3. API Image Enhancement Processing

The image enhancement are each stored in `processing.py`. They are modular to allow for scalability and customizability. 
Adding a image enhancment is as simple as creating a function that accepts a numpy array as a parameter and returns the modified array. All that needs to be added to get the enhancement operational are the function decorators `@enhancement_metadata` & `@time_enhancement`.

```python
@enhancement_metadata(
    "White Balance Correction",
    "Applies white balance correction to enhance the color balance in the image.",
)
@time_enhancement
def white_balance(image):
    # processing code
    return image
```

`@enhancement_metadata` accepts two parameters, name & description. This decorator defines what the available enhancements are and what will be sent from the `/options` endpoint.

`@time_enhancement` optional decorator that accepts no parameters. This decorator adds the timing functionality to the enhancements and returns the result of the enhancment along with the elapsed seconds (float) for the enhancement as a list. 

e.g.
```json
{
  "white_balance": 0.009001,
  "richard_lucy_deconvolution": 2.695312,
  "adaptive_histograph_equalisation": 0.141962
}
```

The enhancements process the image in a specific order to provide the best results. As python runs code sequentially the logic is setup so that the function order matters. This means that if the functions are ordered `white_balance` then `super_res_upscale` they will conform to that order during the image enhancement process.  

### 4. Client

The client is composed of two primary parts, the UI modules and the IOT modules (somewhat of a backend). There is a separation here for the specific purpose of allowing the abstract methods and functions to be used seprate to the UI. This enables IOT devices to use the same methods as the SeaingClearly Workbench to access the SeaServer API, do various formatting & pre-process images.

#### UI (frontend)

The UI itself is composed of modular parts such as the file selection panel, settings panel, and viewer panel. This modularity makes the code easily readable, quick to debug and simple to configure and modify.   

The UI uses a self-built theming framework that allows the easy customizability of pyside components and efficient and dynamic styling (refer `styler.py`). Component colours and templates can be configured all from the `config.py` file. 

```json 
colours = {
    "bg-primary": "#181818",
    "bg-secondary": "#636363",

    "text-primary": "#f2f2f2",
    "text-secondary": "#919191",

    "border": "#333",
    "border-focus": "#636363",
    ...
}

template_styles = {
    "primary-background" : {
        "background-color": colours['bg-primary']
    },
    "secondary-background" : {
        "background-color": colours['bg-secondary']
    },
    ...
}
```

Required UI settings and assets are also stored the in `config.py` file allowing for future developers to easily change the type of files filtered for the preview list and the assets used by the program such as icons and imagery. 

```json
asset_paths = {
    "prawn": r"assets\prawn\prawn.png",
    "folder": r"assets\folder.png",
}

settings = {
    "file_match_pattern" : [r"*.mp4", r"*.avi", r"*.mov", r"*.jpg", r"*.jpeg", r"*.png", r"*.gif"],
}
```

These items setup a good base for the future of the deliverable, allowing it to scale as processes and technology evolves. 

#### Services & Methods ('backend' - SeaingService)

The services and methods used by the UI abstract key methods enabling semi-complex tasks such as authentication, image enhancement, pre-processing and configuration management to be handled by easy to use functions. Threading is integrated into some of the asynchronous functions to allow for a seamless UI experience. 

A large reason for abstraction is to enable the adapability of methods for IOT devices. 
