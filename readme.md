Code for talk at PyMNtos - Twin Cities Python User Group:

- **Build a simple web app with HTMX and WebSockets**

A bookmark app that streams updates to connected clients using WebSockets.

**[Slides for the talk are here.](https://docs.google.com/presentation/d/11gNDK99DGu5laj6nQdh5dxYqIu7ycOX7Y-KO2KJLwhQ/edit?usp=sharing)**

https://github.com/dan-osull/python_htmx_websockets_demo/assets/47532371/c41a1f9b-3121-480e-bfee-14aa8aff7880

### Useful commands

Run (Docker):

    docker compose up -d

Run (Poetry):

    poetry run uvicorn src.main:app

Lint:

    poetry run black . && poetry run ruff . --fix
    
