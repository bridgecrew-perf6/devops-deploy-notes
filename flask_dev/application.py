from app import create_app


if __name__ == "__main__":
    # apparently you have to run Flask server on localhost so it can be accessed from within a container
    application = create_app()
    application.run(host="0.0.0.0", port=5001, debug=True)
