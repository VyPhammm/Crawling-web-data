# Crawling-web-data

This project is designed to scrape job data from the German Agency's job search portal, process and transform the data, and prepare it for loading into a database.

## Technical
- Selenium
- Python

## Project Structure

```
Crawling-web-data/
│
├── README.md
├── data/
│   └── data.json
└── scripts/
		├── crawling.py
		├── handle_missing_info.py
		├── load_to_db.py
```

## Components

- **scripts/crawling.py**  
	Scrapes job data from the target website and saves the results to `data/data.json`.

- **scripts/handle_missing_info.py**  
	Handles missing or incomplete information in the scraped data, ensuring data quality and consistency.

- **scripts/load_to_db.py**  
	Loads the cleaned and processed data into a cloud database.

- **data/data.json**  
	Stores the raw or processed job data in JSON format.

## How to Use

1. **Install Dependencies**  
	 Make sure you have Python 3.x installed.  
	 Install required packages (e.g., `requests`, `selenium`, `selenium-wire`, etc.):

	 ```powershell
	 pip install -r requirements.txt
	 ```

2. **Scrape Data**  
	 Run the crawler to fetch job data:

	 ```powershell
	 python scripts/crawling.py
	 ```

	 The output will be saved to `data/data.json`.

3. **Handle Missing Information**  
	 Clean and process the data:

	 ```powershell
	 python scripts/handle_missing_info.py
	 ```

4. **Load Data to Database**  
	 Load the processed data into your cloud database:

	 ```powershell
	 python scripts/load_to_db.py
	 ```

## Target Website

- [Arbeitsagentur Job Search](https://www.arbeitsagentur.de/jobsuche/suche?angebotsart=4&ausbildungsart=0&arbeitszeit=vz&branche=22;1;2;9;3;5;7;10;11;16;12;21;26;15;17;19;20;8;23;29&veroeffentlichtseit=7&sort=veroeffdatum)

## Notes

- The project uses Selenium and Selenium Wire for web scraping, which may require a compatible web driver (e.g., ChromeDriver or GeckoDriver).

