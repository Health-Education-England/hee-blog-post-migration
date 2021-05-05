import glob
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def get_title(article):
    title = article.find('h1', {'class': 'entry-title'}).find('a', {'rel': 'bookmark'})

    if title is None:
        title = article.find('h1', {'class': 'entry-title'})

    return title.string if title is not None else ''

def get_author(article):
    author = article.find('a', {'rel': 'author'})
    return author.string if author is not None else ''

def get_categories(article):
    categoryLinks = article.find_all('a', {'rel': 'tag'})
    return [str(categoryLink.string) for categoryLink in categoryLinks]

def get_publication_date_time(article):
    publication_date_time = article.find('time', {'class': 'entry-date'})
    return publication_date_time['datetime'] if publication_date_time is not None else None

def get_copy(article, base_url):
    main_content = article.find('div', {'class': 'entry-content'})

    if main_content is not None:
        # Remove social share section from the main content
        social_share_div_element = main_content.find('div', {'class': ['addtoany_share_save_container', 'addtoany_content', 'addtoany_content_bottom']})

        if social_share_div_element:
            social_share_div_element.decompose()

        # Remove all script tags from the main content (as brXM doesn't support including it in the CKEditor OOTB)
        for script_element in main_content.find_all('script'):
            script_element.decompose()

        # Resolve links with fully qualified URLs
        for link in main_content.find_all('a'):
            link['href'] = urljoin(base_url, link.get('href'))

        # Resolve image src with fully qualified URLs
        for img in main_content.find_all('img'):
            img['src'] = urljoin(base_url, img.get('src'))

        # Add newline between main content items
        copy = f'\n'.join([str(main_content_item) for main_content_item in main_content.findChildren()])

        return copy

    return ''

def has_script_in_copy(article):
    scripts = article.find('div', {'class': 'entry-content'}).find_all('script')

    if len(scripts):
	    return True

    return False

def has_image_in_copy(article):
    images = article.find('div', {'class': 'entry-content'}).find_all('img')
    if len(images):
	    return True

    return False

def extract_blog_post(article, base_url):
    return {
        'title': get_title(article),
        'author': get_author(article),
        'categories': get_categories(article),
        'publication_date_time': get_publication_date_time(article),
        'has_image': has_image_in_copy(article),
        'has_script': has_script_in_copy(article),
        'copy': get_copy(article, base_url)
    }

def extract_posts_and_categories(blog_post_archive_dir, base_url, DEBUG):
    blog_posts = []
    blog_categories = set()

    # Find the path of all HTML files avaiable under ${blog_post_archive_dir}
    for filename in glob.iglob(blog_post_archive_dir + '**/*.html', recursive=True):
        if DEBUG:
            print(f'Processing => {filename}')

        with open(filename) as fp:
            soup = BeautifulSoup(fp, 'html.parser')

            for article in soup.find_all('article'):
                blog_post = extract_blog_post(article, base_url)
                blog_posts.append(blog_post)
                blog_categories |= set(blog_post['categories'])

    return {
        'blog_posts': blog_posts,
        'blog_categories': blog_categories
    }