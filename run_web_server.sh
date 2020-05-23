trap "exit" INT TERM ERR
trap "kill 0" EXIT

GAME_DIR=$(pwd)

cd $GAME_DIR/server && python app.py > $GAME_DIR/server.log &
cd $GAME_DIR/client && npm run serve > $GAME_DIR/client.log &

wait