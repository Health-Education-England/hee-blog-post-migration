import re
from sortedcontainers import SortedDict


def replace_blog_category_labels_with_keys(blog_posts, cumulative_blog_categories_dict):
    for blog_post in blog_posts:
        blog_post['categories'] = [k for k, v in cumulative_blog_categories_dict.items() if v in blog_post['categories']]

def get_cumulative_blog_categories_dict(blog_categories, existing_blog_categories):
    cumulative_blog_categories = {}

    # Adds category key & label for archived blog categories
    for category in blog_categories:
        formatted_category_key = category.replace('&', '_and_')
        formatted_category_key = re.sub(r'[/\.]+', '_', formatted_category_key)
        formatted_category_key = re.sub(r'[^A-Za-z0-9 _-]+', '', formatted_category_key)
        cumulative_blog_categories |= {formatted_category_key.lower().replace(' ', '_'): category.replace('"', '')}

    # Adds category key & label for existing brXM blog categories (supplied)
    for category_key, category_label in existing_blog_categories.items():
        cumulative_blog_categories |= {category_key: category_label}

    return SortedDict(cumulative_blog_categories)