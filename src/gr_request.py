# pylint: disable=all
import requests
import re
import unicodedata
from bs4 import BeautifulSoup


'''
Get book information, including rating, rating count, and summary.
Additional logic to get reviews will be included later
'''
def get_book_reviews(ISBN):
    api_url = f'https://www.goodreads.com/book/isbn/{ISBN}'
    
    try:
        response = requests.get(api_url)
        print(f"Response status code: {response.status_code}")
        response.raise_for_status()
        
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        
        rating_section = soup.find('div', class_='BookPageMetadataSection__ratingStats')
        rating = rating_section.find('div', class_='RatingStatistics__rating').get_text().strip()
        rating_count = rating_section.find('div', class_='RatingStatistics__meta').get_text().strip()
        
        split_text = re.split(r'(ratings)', rating_count)
        rating_count = [unicodedata.normalize('NFKC',split_text[0][:-1]), split_text[1]]

        # Extracting the book summary
        description_section = soup.find('div', class_='DetailsLayoutRightParagraph__widthConstrained')
        summary = description_section.get_text().strip()
        
        return(rating,rating_count,summary,api_url)
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching book information: {e}")
        return None

# Tests
# print(get_book_reviews('9781439550052')[2])
# get_book_reviews('978-1-60309-502-0')
# get_book_reviews('978-1-60309-500-6')
# get_book_reviews('978-1-60309-453-5')
# get_book_reviews('978-1-60309-444-3')
# get_book_reviews('978-1-60309-429-0')
