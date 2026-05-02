# Upwork Skill Analyzer & Automation Dashboard

## Overview

Part of optimizing an Upwork profile is knowing exactly which skill tags clients are using for specific niches. Clients often aren't aware of industry-standard skill names and tend to use generalized terms. 

This project solves that problem. It allows you to enter an Upwork search URL, automatically scrapes each job posting from that URL, and extracts all the tagged skills. The included web dashboard then aggregates and visualizes this data, giving you a ranked breakdown of the most commonly used skills in your target niche. 

By using the exact skill tags clients use in their job postings, you can optimize your Upwork profile and proposals to rank higher in searches and match with more relevant jobs.

## Features

- **Automated Upwork Scraping**: Enter a target Upwork search URL to automatically scrape job postings and their associated skill tags.
- **Data Aggregation**: Saves the extracted job titles, links, and tagged skills directly into an Excel spreadsheet (`upwork_jobs.xlsx`).
- **Analytics Dashboard**: A local web application that visualizes the scraped data.
- **Skill Ranking**: Instantly see which skills are most frequently tagged for a specific niche, helping you identify exactly what keywords to use on your profile.
- **User-Friendly Launchers**: Included `.bat` (Windows) and `.command` (Mac) scripts make it easy to start the application with a single click.

## Prerequisites

- Python 3.10+
- Google Chrome browser (required for the scraper)

## Installation

1. Clone or download this repository to your local machine.
2. Ensure you have Python installed.
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

*(Note: Depending on your Python setup, you may want to set up a virtual environment first, or use `pip3` instead of `pip`)*

4. Create a `.env` file in the root directory if one does not exist, and add any required environment variables (e.g., specific wait times, browser profiles, etc., depending on your implementation).

## Usage

### Starting the Dashboard

The easiest way to start the application is by using the provided launcher scripts:
- **Windows**: Double-click `Start Dashboard.bat`
- **Mac/Linux**: Run `Start Dashboard.command`

Alternatively, you can manually run the dashboard from your terminal:
```bash
python app.py
```
*(Use `python3` if required by your OS)*

### Using the Tool

1. Open the dashboard in your web browser (usually at `http://127.0.0.1:5000` or whatever address is shown in the terminal).
2. Use the **Scrape Data** or **New Search** feature in the dashboard to input an Upwork search URL (e.g., a search for "Python Developer" or "Graphic Design").
3. The scraper will launch in the background, navigate through the job postings on that URL, and extract the required data.
4. Once the scraping is complete, the dashboard will update to show an interactive chart or list ranking the top skills used in those job postings.
5. Use these insights to update your Upwork profile tags!

## Technologies Used

- **Python**: Core automation and data processing.
- **Flask**: Lightweight web framework for the analytics dashboard.
- **Selenium / Undetected-Chromedriver**: Web scraping to navigate Upwork and avoid bot detection.
- **Pandas / OpenPyXL**: Data manipulation and saving to Excel.
- **Plotly**: Interactive data visualization on the dashboard.

## Disclaimer

This tool is intended for personal research and profile optimization. Please be mindful of Upwork's Terms of Service regarding automated access and web scraping. Avoid aggressive scraping that could put your account or IP address at risk.
