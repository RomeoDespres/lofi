# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/RomeoDespres/lofi/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                               |    Stmts |     Miss |   Cover |   Missing |
|----------------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| alembic/env.py                                                                     |       17 |        0 |    100% |           |
| alembic/versions/2b80c7ddb34b\_add\_label\_is\_indie.py                            |       15 |        0 |    100% |           |
| alembic/versions/4b7adbd648dc\_add\_snapshot\_playlist\_relationship.py            |       14 |        0 |    100% |           |
| alembic/versions/7a960d8298ac\_add\_label\_playlist\_image.py                      |       10 |        0 |    100% |           |
| alembic/versions/8adb8a331f45\_add\_snapshot\_table.py                             |       10 |        0 |    100% |           |
| alembic/versions/34f171ff838a\_add\_tables.py                                      |       28 |        0 |    100% |           |
| alembic/versions/55c3b8dbf877\_add\_indexes\_on\_track\_album\_id\_and\_album\_.py |       20 |        0 |    100% |           |
| alembic/versions/69b27895941f\_add\_snapshot\_playlist\_id\_index.py               |       16 |        0 |    100% |           |
| alembic/versions/98eebf462d75\_add\_artist\_image.py                               |       18 |        0 |    100% |           |
| alembic/versions/5319ad355973\_add\_label\_is\_lofi.py                             |       10 |        0 |    100% |           |
| alembic/versions/73619481350c\_add\_editorial\_playlists.py                        |       36 |        0 |    100% |           |
| alembic/versions/bf18360a3ed8\_add\_filtering\_playlists.py                        |       22 |        0 |    100% |           |
| alembic/versions/fcba2a965e33\_add\_popularity\_to\_streams\_reference\_.py        |       10 |        0 |    100% |           |
| alembic/versions/ffad2d23c8ad\_add\_album\_images.py                               |       18 |        0 |    100% |           |
| lofi/\_\_init\_\_.py                                                               |        4 |        0 |    100% |           |
| lofi/db/\_\_init\_\_.py                                                            |        3 |        0 |    100% |           |
| lofi/db/connection.py                                                              |       76 |       24 |     68% |56-70, 94-107 |
| lofi/db/google\_api/\_\_init\_\_.py                                                |        2 |        0 |    100% |           |
| lofi/db/google\_api/credentials.py                                                 |       48 |       23 |     52% |31-33, 37-48, 52-72, 76, 80-85 |
| lofi/db/google\_api/drive.py                                                       |       39 |       25 |     36% |19-20, 25-26, 30-32, 36-46, 50-54, 58-59 |
| lofi/db/models.py                                                                  |       93 |        0 |    100% |           |
| lofi/env.py                                                                        |       12 |        3 |     75% |10, 14, 18 |
| lofi/etl/\_\_init\_\_.py                                                           |        2 |        0 |    100% |           |
| lofi/etl/errors.py                                                                 |        3 |        0 |    100% |           |
| lofi/etl/log.py                                                                    |        2 |        0 |    100% |           |
| lofi/etl/main.py                                                                   |      243 |      178 |     27% |46-61, 76-80, 84-87, 91-101, 105-117, 121-124, 128-130, 134-137, 141-147, 151, 155-166, 170-184, 188-190, 194-195, 255-256, 260-266, 270-271, 276-278, 282-288, 293-303, 307-308, 312-317, 321-335, 339-342, 346-352, 356-370, 374-379, 383-419, 429-431, 435-438, 447-460, 464-465, 469-483, 493-495 |
| lofi/log.py                                                                        |       14 |        0 |    100% |           |
| lofi/spotify\_api/\_\_init\_\_.py                                                  |        3 |        0 |    100% |           |
| lofi/spotify\_api/cache\_handler.py                                                |       27 |        0 |    100% |           |
| lofi/spotify\_api/client.py                                                        |      155 |       25 |     84% |138-148, 157-163, 204-206, 224-225, 229-230, 240-242, 251-258 |
| lofi/spotify\_api/errors.py                                                        |        5 |        0 |    100% |           |
| lofi/spotify\_api/log.py                                                           |        2 |        0 |    100% |           |
| lofi/spotify\_api/models.py                                                        |       65 |        1 |     98% |        80 |
| lofi/spotify\_api/token.py                                                         |        2 |        0 |    100% |           |
| lofi/spotify\_api/tracklist\_utils.py                                              |       59 |        0 |    100% |           |
|                                                                          **TOTAL** | **1103** |  **279** | **75%** |           |


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