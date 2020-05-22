trap "exit" INT TERM ERR
trap "kill 0" EXIT

GAME_DIR=$(pwd)

cd $GAME_DIR/server && python app.py &
cd $GAME_DIR/client && npm run serve &

wait