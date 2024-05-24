import requests
from bs4 import BeautifulSoup
import csv
import argparse
import sys
import re
import time
from collections import defaultdict
from colorama import init, Fore, Style

# Initialize colorama
init()


def validate_url(url):
    # Validate if the URL matches the expected Letterboxd format.
    pattern = re.compile(r'^(https?://)?(www\.)?letterboxd\.com/.*$')
    return re.match(pattern, url) is not None


def find_highest_paginate_pages_number(url):
    # Find the highest page number in the paginate-pages element.
    response = requests.get(url)
    if response.status_code != 200:
        print(Fore.RED + f"Failed to retrieve URL: {response.status_code}" + Style.RESET_ALL)
        sys.exit(1)

    soup = BeautifulSoup(response.content, 'html.parser')
    paginate_elements = soup.find_all('div', class_='paginate-pages')

    max_page_number = 0
    for element in paginate_elements:
        page_numbers = [int(a.get_text()) for a in element.find_all('a') if a.get_text().isdigit()]
        if page_numbers:
            max_page_number = max(max_page_number, max(page_numbers))

    return max_page_number if max_page_number > 0 else 1


def scrape_letterboxd_watchlist(url, total_pages, is_user):
    # Scrape movie information from each page of the Letterboxd watchlist.
    movies = defaultdict(lambda: {"title": "", "link": "", "count": 0})

    for page in range(1, total_pages + 1):
        paginated_url = f"{url}page/{page}/" if page > 1 else url
        if is_user:
            print(
                Fore.GREEN + f"Processing the watchlist of {url.split('/')[-3]}, page {page} of {total_pages}...      "
                             f"                                                      " + Style.RESET_ALL,
                end="\r")
        else:
            print(
                Fore.GREEN + f"Processing the list {url.split('/')[-2]}, page {page} of {total_pages}...              "
                             f"                                              " + Style.RESET_ALL,
                end="\r")
        response = requests.get(paginated_url)
        if response.status_code != 200:
            print(
                Fore.RED + f"\nFailed to retrieve URL: {response.status_code}                                                            " + Style.RESET_ALL)
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all div elements that contain the class 'really-lazy-load poster'
        for item in soup.select('div[class*="really-lazy-load poster"]'):
            film_id = item.get('data-film-id')
            link = 'https://letterboxd.com' + item.get('data-target-link')
            img_tag = item.find('img', class_='image')
            if link and img_tag and 'alt' in img_tag.attrs:
                title = img_tag['alt']
                movies[film_id]["title"] = title
                movies[film_id]["link"] = link
                movies[film_id]["count"] += 1

        time.sleep(0.3)  # Wait for 300 milliseconds to avoid rate limiting
    return movies


def get_film_details(film_url):
    # Scrape extra information about a film.
    response = requests.get(film_url)
    if response.status_code != 200:
        print(Fore.RED + f"Failed to retrieve URL: {film_url}" + Style.RESET_ALL)
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')

    details = {'Year': soup.find('div', class_='releaseyear').get_text().strip() if soup.find('div',
                                                                                              class_='releaseyear') else 'N/A',
               'Director': soup.find('p', class_='credits').find('span', class_='prettify').get_text() if soup.find(
                   'p', class_='credits') and soup.find('p', class_='credits').find('span',
                                                                                    class_='introduction') else 'N/A',
               'Tagline': soup.find('h4', class_='tagline').get_text().strip() if soup.find('h4',
                                                                                            class_='tagline') else 'N/A',
               'Plot': soup.find('div', class_='truncate').get_text().strip() if soup.find('div',
                                                                                           class_='truncate') else 'N/A',
               'Average Rating': soup.find('meta', {'name': 'twitter:data2'})['content'].split()[0] if soup.find('meta',
                                                                                                                 {
                                                                                                                     'name': 'twitter:data2'}) else 'N/A'}

    # Extract runtime from the JavaScript variable
    film_data_script = soup.find('script', string=re.compile(r'var filmData ='))
    if film_data_script:
        film_data_match = re.search(r'var filmData = \{.*?runTime: (\d+)', film_data_script.string)
        if film_data_match:
            runtime = int(film_data_match.group(1))
            details['Runtime'] = f"{runtime // 60}h{runtime % 60}m"
        else:
            details['Runtime'] = 'N/A'
    else:
        details['Runtime'] = 'N/A'

    return details


def output_to_console(movies, fast):
    # Output movie information to the console.
    def truncate(text, length):
        return text[:length] + '...' if len(text) > length else text

    if fast:
        print(Fore.WHITE + "{:<30} {:<60}".format("Title", "URL") + Style.RESET_ALL)
        for film_id, details in movies.items():
            print(
                Fore.WHITE + "{:<30} {:<60}".format(truncate(details['title'], 30), details['link']) + Style.RESET_ALL)
    else:
        print(Fore.WHITE + "{:<30} {:<60} {:<4} {:<25} {:<55} {:<6} {:<8}".format("Title", "URL", "Year", "Director",
                                                                                  "Plot", "Rating",
                                                                                  "Runtime") + Style.RESET_ALL)
        for film_id, details in movies.items():
            extra_details = get_film_details(details['link'])
            print(Fore.WHITE + "{:<30} {:<60} {:<4} {:<25} {:<55} {:<6} {:<8}".format(
                truncate(details['title'], 30),
                details['link'],
                truncate(extra_details.get('Year', 'N/A'), 4),
                truncate(extra_details.get('Director', 'N/A'), 20),
                truncate(extra_details.get('Plot', 'N/A'), 50),
                truncate(extra_details.get('Average Rating', 'N/A'), 4),
                truncate(extra_details.get('Runtime', 'N/A'), 8)) + Style.RESET_ALL)


def output_to_csv(movies, filename, fast):
    # Output movie information to a CSV file.
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if fast:
            writer.writerow(["Film ID", "Title", "URL", "Count"])
            for film_id, details in movies.items():
                writer.writerow([film_id, details['title'], details['link'], details['count']])
        else:
            writer.writerow(
                ["Film ID", "Title", "URL", "Year", "Director", "Plot", "Average Rating", "Runtime", "Count"])
            for film_id, details in movies.items():
                extra_details = get_film_details(details['link'])
                writer.writerow([
                    film_id,
                    details['title'],
                    details['link'],
                    extra_details.get('Year', 'N/A'),
                    extra_details.get('Director', 'N/A'),
                    extra_details.get('Plot', 'N/A'),
                    extra_details.get('Average Rating', 'N/A'),
                    extra_details.get('Runtime', 'N/A'),
                    details['count']
                ])


def main():
    parser = argparse.ArgumentParser(description='Scrape a Letterboxd watchlist and output the data.')
    parser.add_argument('-l', '--list', action='append', type=str, help='Letterboxd list URL to use')
    parser.add_argument('-u', '--user', action='append', type=str,
                        help='Letterboxd username to process their watchlist')
    parser.add_argument('-o', '--output', type=str, help='Output filename (CSV format)')
    parser.add_argument('-c', '--count', type=int,
                        help='Minimum number of occurrences a film must appear in lists to be included')
    parser.add_argument('-f', '--fast', action='store_true', help='Skip pulling extra film information')

    args = parser.parse_args()

    # Validate input arguments
    if not args.list and not args.user:
        print(Fore.RED + "At least one --list or --user option must be provided." + Style.RESET_ALL)
        sys.exit(1)

    if args.output and not args.output.endswith('.csv'):
        print(Fore.RED + "Output filename must be a CSV file." + Style.RESET_ALL)
        sys.exit(1)

    urls = []
    if args.list:
        urls.extend(args.list)
    if args.user:
        for user in args.user:
            urls.append(f"https://letterboxd.com/{user}/watchlist/")

    all_movies = defaultdict(lambda: {"title": "", "link": "", "count": 0})

    for url in urls:
        if not validate_url(url):
            print(Fore.RED + f"Invalid URL: {url}. Skipping..." + Style.RESET_ALL)
            continue

        total_pages = find_highest_paginate_pages_number(url)

        is_user = 'watchlist' in url
        movies = scrape_letterboxd_watchlist(url, total_pages, is_user)
        for film_id, details in movies.items():
            all_movies[film_id]["title"] = details["title"]
            all_movies[film_id]["link"] = details["link"]
            all_movies[film_id]["count"] += details["count"]

    min_count = args.count if args.count else len(urls)

    filtered_movies = {film_id: details for film_id, details in all_movies.items() if details["count"] >= min_count}

    if not filtered_movies:
        max_count = max(all_movies.values(), key=lambda x: x["count"])["count"]
        print(
            Fore.YELLOW + f"No films found with at least {min_count} occurrences. Showing films with highest "
                          f"occurrences ({max_count}):" + Style.RESET_ALL)
        filtered_movies = {film_id: details for film_id, details in all_movies.items() if details["count"] == max_count}

    if args.output:
        output_to_csv(filtered_movies, args.output, args.fast)
    else:
        output_to_console(filtered_movies, args.fast)


if __name__ == "__main__":
    main()
