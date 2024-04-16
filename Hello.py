import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

@st.cache
def get_all_links(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()
        base_url = response.url
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            if full_url.startswith(base_url):  # Changed to use base_url
                links.add(full_url)
        return links
    else:
        st.error("Failed to fetch page.")
        return set()

@st.cache
def get_text_data(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        exclude_elements = ['script', 'style', 'meta', 'link', 'noscript', 'head']
        formatted_text = set()  # Using a set to avoid duplicate data
        for element in soup.find_all(
            ['p', 'h1', 'h2', 'h3', 'li', 'div', 'strong', 'em', 'ul', 'ol']):
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                formatted_text.add('\n' + element.get_text(strip=True) + '\n\n')
            elif element.name in ['ul', 'ol']:
                list_items = element.find_all('li')
                for item in list_items:
                    formatted_text.add('\n' + item.get_text(strip=True) + '\n')
            else:
                formatted_text.add('\n' + element.get_text(strip=True) + '\n\n')
        
        return ''.join(formatted_text)  # Convert set to string
    else:
        return ""

def crawl_and_save(url, max_depth, visited_links=set()):
    if max_depth == 0:
        return
    
    links = get_all_links(url)
    crawled_text = ""
    
    for link in links:
        if link not in visited_links:
            visited_links.add(link)
            text_data = get_text_data(link)
            crawled_text += text_data + "\n"  # Concatenate text data
            st.write(text_data)
            crawl_and_save(link, max_depth - 1, visited_links)
    
    return crawled_text

def main():
    st.title(' Web Crawler')

    site_url = st.text_input('Enter website URL:')
    max_depth = st.slider('Select max depth:', min_value=1, max_value=10, value=6)

    if st.button('Start Crawling') and site_url:
        st.write(f"Crawling {site_url} up to depth {max_depth}...")
        crawled_text = crawl_and_save(site_url, max_depth)
        
        # Download text data as .txt file
        if crawled_text:
            st.download_button(
                label="Download Text",
                data=crawled_text.encode('utf-8'),
                file_name="crawled_text.txt",
                mime="text/plain"
            )
            st.success("Text data downloaded successfully!")

if __name__ == "__main__":
    main()
