## Overview

This project is just one repository from a system of microservices that create Minerva, a data platform solution that aims to promote Health, Safety, Security and Environment regulations in Guyana. The other projects are located at:

- https://github.com/shomari11/Minerva_Whatsapp | A Whatsapp bot for reporting
- https://github.com/AndrewGY/Minerva | The Main App for User Interaction
- https://github.com/AndrewGY/MInerva-Detect | A service that utilises YOLO (You Only Look Once) computer vision object detection model for detecting HSSE infringements

## To Run

Install necessary dependencies and run, each in a separate terminal and port
```
python ./fb_module/api.py # runs on port 5000
```
```
python -m fb_module
```
```
python ./scraper/api.py # runs on port 5002
```
```
python -m scraper
```
```
python -m ./cv_module/api.py # runs on port 5001
```
