import requests
from bs4 import BeautifulSoup
import pandas as pd

sp_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

def get_tickers(url):

    # Send a GET request
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the first table on the page
    table = soup.find('table')

    # Extract all rows from the table
    rows = table.find_all('tr')

    # Extract the symbols from the second column of each row
    symbols = [row.find_all('td')[0].text.strip() for row in rows[1:]]

    return symbols

tickers = get_tickers(sp_url)

for i, symbol in enumerate(tickers):
  if "." in symbol:
    tickers[i] = symbol.replace(".", "-")

def chunk_text(text, chunk_size=1400):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) <= chunk_size:
            current_chunk.append(word)
            current_length += len(word) + 1  # +1 for the space
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word) + 1

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def extract_text_from_url(url):
    # need to add header
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract and return the text
        return soup.get_text()
    else:
        return f"Error: Unable to access the URL (status code: {response.status_code})"

# The big kahuna
def download_proxy(tickers):
    chunks = []
    metadata = []
    for ticker in tickers:
        print(f'Now on: {ticker}')
        base_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=DEF+14A&dateb=&owner=exclude&count=40"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
        }
        response = requests.get(base_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch data for {ticker}. Status code: {response.status_code}")
            continue
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', class_='tableFile2')
        if not table:
            print(f"Failed to find the table containing proxy statements for {ticker}.")
            continue
        rows = table.find_all('tr')
        if len(rows) <= 1:
            print("No rows found in the table.")
            continue
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) > 3:
                filing_date = cells[3].text.strip()
                filing_url = 'https://www.sec.gov' + cells[1].a['href']
                if '2023' in filing_date:
                    response = requests.get(filing_url, headers=headers)
                    if response.status_code != 200:
                        print(f"Failed to fetch proxy statement for {ticker}. Status code: {response.status_code}")
                        continue
                    # Parse the HTML content
                    html_soup = BeautifulSoup(response.content, 'html.parser')
                    html_link = html_soup.find('a', {'href': lambda x: x and ('def14a' in x or ticker.lower() in x.lower()) and x.endswith('.htm')})
                    print(html_link)
                    if html_link:
                        document_url = 'https://www.sec.gov' + html_link['href']
                        if '/ix?doc=' in document_url:
                            document_url = 'https://www.sec.gov/' + document_url.split('/ix?doc=')[1]
                        print(f"Document URL: {document_url}")
                        text = extract_text_from_url(document_url)
                        if text:
                            file_chunks = chunk_text(text)
                            print(f"Number of chunks for {ticker}: {len(file_chunks)}")
                            # Add chunked text to metadata
                            for i, chunk in enumerate(file_chunks):
                                metadata.append({
                                    'filing_date': filing_date,
                                    'ticker': ticker,
                                    'chunk_id': i+1,
                                })
                            chunks.extend(file_chunks)

        df = pd.DataFrame({'id': range(len(chunks)), 'text': chunks, 'metadata': metadata})
    return df

data = download_proxy(tickers)

data['id'] = data['id'].astype(str)