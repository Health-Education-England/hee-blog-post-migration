import os
import json
from ruamel.yaml import YAML
import blog_category_util
import blog_extractor as extractor
import blog_brxm_yaml_decorator as decorator


# The input directory must end with '/' suffix
INPUT_BLOG_EXPLODED_POST_ARCHIVE_PATH = '/input/'

# Output
OUTPUT_BRXM_BLOG_CATEGORIES_YAML_FILE = '/output/brxm-archived-blog-categories.yaml'
OUTPUT_BRXM_BLOG_POST_YAML_FILE = '/output/brxm-archived-blog-posts.yaml'
OUTPUT_BLOG_POSTS_NOTES_TXT_FILE = '/output/blog-posts-notes.txt'

def dump_brxm_yaml_file(decorated_yaml_object, yaml_file_path):
    yaml = YAML()
    yaml.indent(offset = 2)
    yaml.representer.ignore_aliases = lambda *data: True

    with open(yaml_file_path, 'w') as file:
        yaml.dump(decorated_yaml_object, file)

def dump_blog_post_notes(blog_posts, txt_file_path):
    # General notes
    notes = "General Notes [Applicable for all archived blog posts]: The data for the following brXM fields aren't available in the archive. Suggest Editor to add data for the missing fields if required.\n"
    notes += "- Summary [Required]\n"
    notes += "- Last Reviewed\n"
    notes += "- Next Reviewed\n"
    notes += "- Quick Links\n\n\n"

    # Notes for blog posts containing images
    blog_posts_containing_images = f'\n'.join([f'- {blog_post["title"]}' for blog_post in blog_posts if blog_post['has_image']])

    if blog_posts_containing_images:
        notes += f'Archived blog posts containing images: Suggest Editor to upload the Image(s) manually onto brXM and associate them to the appropriate blog posts.\n{blog_posts_containing_images}\n\n\n'


    blog_posts_containing_scripts = f'\n'.join([f'- {blog_post["title"]}' for blog_post in blog_posts if blog_post['has_script']])

    if blog_posts_containing_scripts:
        notes += f'Archived blog posts that originally had scripts: OOTB, brXM doesn\'t allow Editor to include scripts within Rich Text Editor and so the scripts have been stripped off. Suggest Editor to remove any script associated content from the Copy.\n{blog_posts_containing_scripts}\n\n\n'

    # Notes for blog posts that originally had publication date
    blog_posts_not_containing_publication_date_time = f'\n'.join([f'- {blog_post["title"]}' for blog_post in blog_posts if blog_post['publication_date_time'] is None])

    if blog_posts_not_containing_publication_date_time:
        notes += f'Archived blog posts containing no publication date & time: Currently, these blog posts are defaulted with date & time and suggest Editor to update them with appropriate publication date & time.\n{blog_posts_not_containing_publication_date_time}'

    with open(txt_file_path, 'w') as file:
        file.write(notes)

def main():
    # Input
    INPUT_BLOG_POST_COPY_LINK_BASE_URL = os.getenv('INPUT_BLOG_POST_COPY_LINK_BASE_URL')
    EXISTING_BLOG_CATEGORIES = json.loads(os.getenv('INPUT_BRXM_EXISTING_BLOG_CATEGORIES_JSON'))
    DEBUG = eval(os.getenv('DEBUG'))

    # Extract archived blog posts
    blog_posts_and_categories = extractor.extract_posts_and_categories(INPUT_BLOG_EXPLODED_POST_ARCHIVE_PATH, INPUT_BLOG_POST_COPY_LINK_BASE_URL, DEBUG)
    blog_categories = blog_posts_and_categories['blog_categories']
    blog_posts = blog_posts_and_categories['blog_posts']
    print(f'There are {len(blog_posts)} blog posts have been extracted')

    if DEBUG:
        print(f'Extracted Blog Categories = {blog_categories}')
        print(f'Extracted Blog Posts = {blog_posts}')

    cumulative_blog_categories_dict = blog_category_util.get_cumulative_blog_categories_dict(blog_categories, EXISTING_BLOG_CATEGORIES)
    blog_category_util.replace_blog_category_labels_with_keys(blog_posts, cumulative_blog_categories_dict)

    # Decorate extracted archived blog posts for brXM import
    decorated_blog_categories = decorator.get_decorated_blog_categories_handle(cumulative_blog_categories_dict)
    decorated_blog_posts = decorator.get_decorated_archived_blog_posts_folder(blog_posts)

    if DEBUG:
        print(f'Decorated Blog Categories = {decorated_blog_categories}')
        print(f'Decorated Blog Posts = {decorated_blog_posts}')

    # Dump decorated archived blog categories (including the ones exists in brXM currently
    # indicated via ${INPUT_BRXM_EXISTING_BLOG_CATEGORIES}) as yaml file
    dump_brxm_yaml_file(decorated_blog_categories, OUTPUT_BRXM_BLOG_CATEGORIES_YAML_FILE)
    print(f'brXM archived blog categories yaml file {OUTPUT_BRXM_BLOG_POST_YAML_FILE} has successfully been generated')

    # Dump decorated archived blog posts as yaml file
    dump_brxm_yaml_file(decorated_blog_posts, OUTPUT_BRXM_BLOG_POST_YAML_FILE)
    print(f'brXM archived blog post yaml file {OUTPUT_BRXM_BLOG_POST_YAML_FILE} has successfully been generated')

    # Dump list of blog posts containing images in its copy
    dump_blog_post_notes(blog_posts, OUTPUT_BLOG_POSTS_NOTES_TXT_FILE)
    print(f'The file {OUTPUT_BLOG_POSTS_NOTES_TXT_FILE} containing arhived blog post notes has successfully been generated')

if __name__ == '__main__':
    main()