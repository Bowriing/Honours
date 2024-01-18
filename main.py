from website import create_app

#run config and setup of app when run
app=create_app()

#run app in debug mode for development
if __name__ == '__main__':
    app.run(debug=True)

