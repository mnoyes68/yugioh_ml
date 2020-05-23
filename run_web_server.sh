trap "exit" INT TERM ERR
trap "kill 0" EXIT

GAME_DIR=$(pwd)

source $GAME_DIR/server/venv/bin/activate

cd $GAME_DIR/server && python app.py > $GAME_DIR/server.log &
cd $GAME_DIR/client && npm run serve > $GAME_DIR/client.log &

wait