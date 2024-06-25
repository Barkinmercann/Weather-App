import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image, ImageTk

api_key = 'd804116e069f85c7895090e234527fe8'
forecast_url = 'https://api.openweathermap.org/data/2.5/forecast?q={}&appid={}&units=metric'
settings_file = '../Weather App/settings.txt'
cities_file = '../Weather App/cities.txt'

temp_mode = 'Celsius'

def load_cities():
    try:
        with open(cities_file, 'r') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

def load_settings():
    try:
        with open(settings_file, 'r') as f:
            data = f.readline().strip()
            if data:
                city, temp = data.split(',')
                return city, temp
            else:
                return None, None
    except FileNotFoundError:
        return None, None

def save_settings(city, temp_mode):
    if city and temp_mode:
        with open(settings_file, 'w') as f:
            f.write(f"{city},{temp_mode}")

def save_city(city):
    cities = load_cities()
    if city and city not in cities:
        with open(cities_file, 'a') as f:
            f.write(f"{city}\n")


def add_new_city():
    global temp_mode
    new_city = cities_combobox.get().strip()
    if new_city and new_city not in load_cities():
        try:
            url = forecast_url.format(new_city, api_key)
            response = requests.get(url)
            response.raise_for_status()
            save_city(new_city)
            cities_combobox.config(values=load_cities())
            save_settings(new_city, temp_mode)
            get_weather()
            error_label.config(text="")
        except requests.RequestException:
            error_label.config(text="Please enter a valid city!", fg="red")
    else:
        error_label.config(text="City already exists or invalid input.", fg="red")

def get_weather():
    global temp_mode
    city = cities_combobox.get()
    if not city:
        return

    url = forecast_url.format(city, api_key)
    response = requests.get(url)
    weather_data = response.json()

    if response.status_code == 200:
        city_label.config(text=weather_data['city']['name'])
        forecast_list = [entry for entry in weather_data['list'] if "12:00:00" in entry['dt_txt']][:3]
        update_temp_label(weather_data['list'][0]['main']['temp'])
        update_forecast_labels(forecast_list)
        update_image(weather_data['list'][0]['weather'][0]['description'])
        error_label.config(text="")
    else:
        city_label.config(text="Error: Unable to fetch weather")
        forecast_label.config(text="Error: Invalid city or API issue")
        desc_label.config(text="")
        error_label.config(text="Please enter a valid city!", fg="red")

def update_temp_label(temp_kelvin):
    if temp_mode == 'Celsius':
        temp_celsius = temp_kelvin
        temp_label.config(text=f"Temperature: {temp_celsius:.2f}°C")
    elif temp_mode == 'Fahrenheit':
        temp_fahrenheit = (temp_kelvin * 9/5) + 32
        temp_label.config(text=f"Temperature: {temp_fahrenheit:.2f}°F")

def toggle_temp_mode():
    global temp_mode
    temp_mode = 'Fahrenheit' if temp_mode == 'Celsius' else 'Celsius'
    toggle_temp_button.config(text=f"Switch to {temp_mode}")
    get_weather()

def update_forecast_labels(forecast_list):
    forecast_text = "\n\n".join([f"{entry['dt_txt'][:10]}: {entry['main']['temp'] if temp_mode == 'Celsius' else (entry['main']['temp'] * 9/5) + 32:.2f}°{temp_mode[0]}, {entry['weather'][0]['description'].capitalize()}"
                                 for entry in forecast_list])
    forecast_label.config(text=forecast_text if forecast_list else "No forecast data available.", font=('Helvetica', 18), bg='#2E2E2E', fg='#FFFFFF')

def update_image(weather):
    path = ""
    if weather == "clear sky":
        path = "../Weather App/Icons/clear_sky.png"
    elif "rain" in weather:
        path = "../Weather App/Icons/rain.png"
    elif weather == "snow":
        path = "../Weather App/Icons/snow.png"
    elif weather == "mist":
        path = "../Weather App/Icons/mist.png"
    elif weather == "few clouds":
        path = "../Weather App/Icons/few_clouds.png"
    elif "clouds" in weather:
        path = "../Weather App/Icons/scattered_clouds.png"
    elif weather == "thunderstorm":
        path = "../Weather App/Icons/thunderstorm.png"

    image = Image.open(path)
    width, height = image.size
    photo = ImageTk.PhotoImage(image.resize((width // 5, height // 5)))
    label1.config(image=photo)
    label1.image = photo

root = tk.Tk()
root.title("Weather App")
root.geometry('1000x600')
root.configure(bg='#2E2E2E')

icon = tk.PhotoImage(file="../Weather App/Icons/app_icon.png")
root.iconphoto(True, icon)

title = tk.Label(root, text="Weather App", font=('Helvetica', 30, 'bold'), bg='#2E2E2E', fg='#FFFFFF')
title.pack(pady=20)

last_city, temp_mode = load_settings()
temp_mode = temp_mode if temp_mode else 'Celsius'

frame = tk.Frame(root, bg='#2E2E2E')
frame.pack(pady=20)

cities_combobox = ttk.Combobox(frame, values=load_cities(), font=('Helvetica', 14), background='#4B4B4B', foreground='#FFFFFF')
cities_combobox.set(last_city)
cities_combobox.grid(row=0, column=0, padx=10, pady=10)

add_city_button = tk.Button(frame, text="Add City", command=add_new_city, font=('Helvetica', 14), bg='#4682B4', fg='#FFFFFF')
add_city_button.grid(row=0, column=1, padx=10, pady=10)

get_weather_button = tk.Button(frame, text="Get Weather", command=get_weather, font=('Helvetica', 14), bg='#4682B4', fg='#FFFFFF')
get_weather_button.grid(row=0, column=2, padx=10, pady=10)

toggle_temp_button = tk.Button(frame, text=f"Switch to {temp_mode}", command=toggle_temp_mode, font=('Helvetica', 14), bg='#4682B4', fg='#FFFFFF')
toggle_temp_button.grid(row=0, column=3, padx=10, pady=10)

error_label = tk.Label(frame, text="", font=('Helvetica', 12), bg='#2E2E2E', fg='red')  # Label to show error messages
error_label.grid(row=1, column=0, padx=10, pady=5)

left_frame = tk.Frame(root, bg='#2E2E2E')
left_frame.pack(side=tk.LEFT, padx=50, pady=20)

city_label = tk.Label(left_frame, font=('Helvetica', 24), bg='#2E2E2E', fg='#FFFFFF')
city_label.pack(pady=10)

temp_label = tk.Label(left_frame, font=('Helvetica', 24), bg='#2E2E2E', fg='#FFFFFF')
temp_label.pack(pady=10)

icon_frame = tk.Frame(left_frame, bg='#2E2E2E')
icon_frame.pack(pady=20)

image1 = Image.open("../Weather App/Icons/app_icon.png")
width, height = image1.size
photo1 = ImageTk.PhotoImage(image1.resize((width // 5, height // 5)))
label1 = tk.Label(icon_frame, image=photo1, bg='#2E2E2E')
label1.grid(padx=10, pady=10)

forecast_frame = tk.Frame(root, bg='#2E2E2E')
forecast_frame.pack(side=tk.RIGHT, padx=50, pady=20)

forecast_label = tk.Label(forecast_frame, font=('Helvetica', 18), bg='#2E2E2E', fg='#FFFFFF')
forecast_label.pack(pady=10)

desc_label = tk.Label(forecast_frame, font=('Helvetica', 24), bg='#2E2E2E', fg='#FFFFFF')
desc_label.pack(pady=10)


def main():
    get_weather()
    root.mainloop()

if __name__ == '__main__':
    main()
