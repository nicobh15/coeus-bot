# pylint: disable=all
import requests

## TODO skip books if title is not within some Levenshtein distance of a response substring
def get_book_info(book_title):
    api_url = f'https://www.googleapis.com/books/v1/volumes?q={book_title}'

    try:
        response = requests.get(api_url)
        print(f"Response status code: {response.status_code}")
        response.raise_for_status()
        books = response.json().get('items', [])
        
        book_details = []
        for book in books[:5]: 
            volume_info = book.get('volumeInfo', {})
            book_data = {
                'title': volume_info.get('title'),
                'authors': volume_info.get('authors', []),
                'publication_year': volume_info.get('publishedDate', '').split('-')[0], 
                'isbns': [identifier['identifier'] for identifier in volume_info.get('industryIdentifiers', []) if identifier['type'] in ['ISBN_10', 'ISBN_13']]
            }
            book_details.append(book_data)

        print(f"Found {len(book_details)} books.")
        return book_details 
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching book information: {e}")
        return None