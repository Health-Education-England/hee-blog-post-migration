import re
import uuid
import unicodedata
from datetime import datetime, timezone
from ruamel.yaml.scalarstring import LiteralScalarString

def get_current_utc():
    return datetime.now(timezone.utc)

def get_brxm_node_name(title):
    normalised_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode()
    non_alpha_numeric_chars_stripped_title = re.sub(r'[^A-Za-z0-9 -]+', '', normalised_title)
    return non_alpha_numeric_chars_stripped_title[:50].lower().replace(' ', '-')

def get_default_decorated_last_next_review_object():
    return {
        'jcr:primaryType': 'hee:pageLastNextReview'
        # 'hee:lastReviewed': get_current_utc(),
        # 'hee:nextReviewed': get_current_utc()
    }

def get_html_content_block(copy):
    return {
        'jcr:primaryType': 'hippostd:html',
        'hippostd:content': LiteralScalarString(copy)
    }

def get_decorated_empty_quick_links_object():
    return {'jcr:primaryType': 'hee:QuickLinks', 'hee:title': ''}


def get_decorated_handle_object(title):
    return {
        'jcr:primaryType': 'hippo:handle',
        'jcr:mixinTypes': ['hippo:named', 'hippo:versionInfo', 'mix:referenceable'],
        'hippo:name': f'{title}'
    }

def get_decorated_archived_blog_posts_folder_object():
    return {
        "jcr:primaryType": "hippostd:folder",
        "jcr:mixinTypes": ["hippo:named", "hippotranslation:translated", "mix:versionable"],
        "hippo:name": "Archived Blog Posts",
        "hippostd:foldertype": ["new-translated-folder", "new-blogPost-document"],
        "hippotranslation:id": str(uuid.uuid4()),
        "hippotranslation:locale": "en"
    }

def get_decorated_blog_post_object(blog_post, state, availability, translation_uuid):
    decorated_blog_post = {}

    # Add meta data
    decorated_blog_post['jcr:primaryType'] = 'hee:blogPost'
    decorated_blog_post['jcr:mixinTypes'] = ['mix:referenceable', 'mix:versionable']
    decorated_blog_post['hippo:availability'] = availability
    decorated_blog_post['hippostd:retainable'] = False
    decorated_blog_post['hippostd:state'] = state
    decorated_blog_post['hippostdpubwf:createdBy'] = 'admin'
    decorated_blog_post['hippostdpubwf:lastModifiedBy'] = 'admin'
    decorated_blog_post['hippostdpubwf:creationDate'] = get_current_utc()
    decorated_blog_post['hippostdpubwf:lastModificationDate'] = get_current_utc()
    decorated_blog_post['hippotranslation:id'] = translation_uuid
    decorated_blog_post['hippotranslation:locale'] = 'en'

    # Add blog data
    decorated_blog_post['hee:title'] = f'{blog_post["title"]}'
    decorated_blog_post['hee:author'] = f'{blog_post["author"]}'
    decorated_blog_post['hee:categories'] = blog_post['categories']
    if blog_post['publication_date_time'] is not None:
        decorated_blog_post['hee:publicationDate'] = datetime.strptime(blog_post['publication_date_time'] , '%Y-%m-%dT%H:%M:%S%z')

    decorated_blog_post['/hee:contentBlocks[1]'] = get_html_content_block(blog_post['copy'])
    decorated_blog_post['/hee:pageLastNextReview'] = get_default_decorated_last_next_review_object()
    decorated_blog_post['/hee:QuickLinks'] = get_decorated_empty_quick_links_object()

    return decorated_blog_post

def get_decorated_archived_blog_posts_folder(blog_posts):
    decorated_archived_blog_posts_folder = {}

    # Build archived-blog-posts folder node
    decorated_archived_blog_posts_folder['/archived-blog-posts'] = get_decorated_archived_blog_posts_folder_object()

    for blog_post in blog_posts:
        brxm_node_name = get_brxm_node_name(blog_post['title'])

        # Build hee:blogPost handle node
        decorated_archived_blog_posts_folder['/archived-blog-posts']['/' + brxm_node_name] = get_decorated_handle_object(blog_post['title'])

        translation_uuid = str(uuid.uuid4())

        # Build hee:blogPost node for draft version
        decorated_archived_blog_posts_folder['/archived-blog-posts']['/' + brxm_node_name]['/' + brxm_node_name + '[1]'] = get_decorated_blog_post_object(blog_post, 'draft', [], translation_uuid)

        # Build hee:blogPost node for unpublished version
        decorated_archived_blog_posts_folder['/archived-blog-posts']['/' + brxm_node_name]['/' + brxm_node_name + '[2]'] = get_decorated_blog_post_object(blog_post, 'unpublished', ['preview'], translation_uuid)

    return decorated_archived_blog_posts_folder

def get_decorated_blog_categories_handle_object():
    return {
        'jcr:primaryType': 'hippo:handle',
        'jcr:mixinTypes': ['hippo:named', 'mix:referenceable'],
        'hippo:name': 'BlogCategories'
    }

def get_decorated_blog_categories_handle(blog_categories):
    decorated_blog_categories_handle = {}

    # Build selection:valuelist handle node for BlogCategories
    decorated_blog_categories_handle['/blogcategories'] = get_decorated_blog_categories_handle_object()

    decorated_blog_categories_value_list = {}
    decorated_blog_categories_value_list['jcr:primaryType'] = 'selection:valuelist'
    decorated_blog_categories_value_list['jcr:mixinTypes'] = ['hippotranslation:translated', 'mix:referenceable']
    decorated_blog_categories_value_list['hippo:availability'] = ['live', 'preview']
    decorated_blog_categories_value_list['hippotranslation:id'] = str(uuid.uuid4())
    decorated_blog_categories_value_list['hippotranslation:locale'] = 'inherited - from query'

    # Builds selection:valuelist nodes on cumulated blog categories
    for count, (category_key, category_label) in enumerate(blog_categories.items(), start = 1):
        decorated_blog_categories_value_list['/selection:listitem[' + str(count) + ']'] = {
            'jcr:primaryType': 'selection:listitem',
            'selection:key': category_key,
            'selection:label': category_label
        }

    decorated_blog_categories_handle['/blogcategories']['/blogcategories'] = decorated_blog_categories_value_list

    return decorated_blog_categories_handle