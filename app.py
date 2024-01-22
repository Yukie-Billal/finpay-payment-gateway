from _app import socketio, app

if __name__ == '__main__':
    socketio.run(debug=True, host='0.0.0.0', app=app)

