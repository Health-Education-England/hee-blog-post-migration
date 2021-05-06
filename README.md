# HEE Blog Post Migration

This project will be used to migrate the existing HEE archived blog posts onto brXM (Bloomreach Experience Manager) platform.

The project essentially extracts blog post data from the given exploded archive and builds YAML files which can readily be imported to brXM.

## Pre Requisites
In order to develop and run on this platform you will need to have the `Docker` installed.

## Run with Docker Compose
Execute the following command to run the script:

```
>> docker-compose up
```

Make sure to update the following volumes and environment variables before running the script:

- Volumes
  - /input: The volume under which exploded blog archive is available.
  - /output: The volume under which the outputs will be stored. The migration script produced the following outputs:
    - brxm-archived-blog-categories.yaml: An export of blog categories which could readily be imported onto brXM as `/content/documents/administration/valuelists/kls/blogcategories` value-list.
    - brxm-archived-blog-posts.yaml: An export of blog posts which could readily be imported onto brXM as `hee:blogPost` documents under `Archived Blog Posts` folder.
    - blog-posts-notes.txt: Contains notes for Editors to perform post migration steps.
- Environment Variables
  - INPUT_BLOG_POST_COPY_LINK_BASE_URL: The Base URL to which the relative links in the blog post copy should be resolved to. This has currently been set to https://kfh.libraryservices.nhs.uk.
  - INPUT_BRXM_EXISTING_BLOG_CATEGORIES_JSON: Stringified JSON containing existing blog categories setup in brXM. This has currently been set to:
  ```
  '{
      "discovery_system": "Discovery System",
      "inter_library_loans": "Inter Library Loans",
      "data_search": "Data Search",
      "document_supply": "Document Supply"
  }'
  ```
  This is to ensure to include the existing blog categories setup in brXM in the `brxm-archived-blog-categories.yaml` output.

## Importing outputs onto brXM
- Login to the brXM console (`/cms/console`) of the environment wherein the blog posts needs to be imported (with `xm.console.user` privilege).
- Import `brxm-archived-blog-categories.yaml` under `/content/documents/administration/valuelists/kls` node in order to import the blog categories.
- Import `brxm-archived-blog-posts.yaml` under `/content/documents/lks` node in order to import blog posts under `Archived Blog Posts` folder.
- Login to brXM CMS (`/cms`) of the environment wherein the blog posts have been imported (with privilege to edit documents of `hee:blogPost` type) and publish all migrated blog post documents by choosing `Publish all in folder...` on `Archived Blog Posts` folder.
- Finally, share `blog-posts-notes.txt` file with HEE Editors to action on post migration steps (if required).