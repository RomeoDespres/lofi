# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/RomeoDespres/lofi/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                        |    Stmts |     Miss |   Cover |   Missing |
|---------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| alembic/env.py                                                              |       18 |        0 |    100% |           |
| alembic/versions/2b80c7ddb34b\_add\_label\_is\_indie.py                     |       15 |        0 |    100% |           |
| alembic/versions/4b7adbd648dc\_add\_snapshot\_playlist\_relationship.py     |       14 |        0 |    100% |           |
| alembic/versions/7a960d8298ac\_add\_label\_playlist\_image.py               |       10 |        0 |    100% |           |
| alembic/versions/8adb8a331f45\_add\_snapshot\_table.py                      |       10 |        0 |    100% |           |
| alembic/versions/34f171ff838a\_add\_tables.py                               |       28 |        0 |    100% |           |
| alembic/versions/5319ad355973\_add\_label\_is\_lofi.py                      |       10 |        0 |    100% |           |
| alembic/versions/73619481350c\_add\_editorial\_playlists.py                 |       36 |        0 |    100% |           |
| alembic/versions/fcba2a965e33\_add\_popularity\_to\_streams\_reference\_.py |       10 |        0 |    100% |           |
| lofi/\_\_init\_\_.py                                                        |        2 |        0 |    100% |           |
| lofi/db/\_\_init\_\_.py                                                     |        3 |        0 |    100% |           |
| lofi/db/connection.py                                                       |       98 |        0 |    100% |           |
| lofi/db/models.py                                                           |       84 |        0 |    100% |           |
| lofi/env.py                                                                 |       14 |        1 |     93% |        22 |
| lofi/etl/\_\_init\_\_.py                                                    |        2 |        0 |    100% |           |
| lofi/etl/errors.py                                                          |        3 |        0 |    100% |           |
| lofi/etl/log.py                                                             |        2 |        0 |    100% |           |
| lofi/etl/main.py                                                            |      216 |      152 |     30% |47-51, 55-58, 62-72, 76-88, 92-95, 99-101, 105-108, 112-119, 123, 127-128, 132-143, 147-161, 165-167, 171-172, 232-233, 237-244, 249-251, 255-261, 266-278, 282-283, 287-301, 305-310, 314-328, 332-335, 339-344, 348-370, 380-382, 386-389, 398-411, 415-416, 420-433, 443-445 |
| lofi/log.py                                                                 |       13 |        0 |    100% |           |
| lofi/spotify\_api/\_\_init\_\_.py                                           |        3 |        0 |    100% |           |
| lofi/spotify\_api/cache\_handler.py                                         |       27 |        0 |    100% |           |
| lofi/spotify\_api/client.py                                                 |      148 |       21 |     86% |134-144, 190-192, 210-211, 215-216, 226-228, 237-244 |
| lofi/spotify\_api/errors.py                                                 |        5 |        0 |    100% |           |
| lofi/spotify\_api/log.py                                                    |        2 |        0 |    100% |           |
| lofi/spotify\_api/models.py                                                 |       61 |        1 |     98% |        75 |
| lofi/spotify\_api/token.py                                                  |        8 |        0 |    100% |           |
| lofi/spotify\_api/tracklist\_utils.py                                       |       61 |        0 |    100% |           |
|                                                                   **TOTAL** |  **903** |  **175** | **81%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/RomeoDespres/lofi/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/RomeoDespres/lofi/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/RomeoDespres/lofi/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/RomeoDespres/lofi/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2FRomeoDespres%2Flofi%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/RomeoDespres/lofi/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.