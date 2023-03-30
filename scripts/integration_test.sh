#!/bin/bash

# Set the number of times to run the test
num_tests=100

# Initialize the counter for successful tests
success_count=0

make docker-compose-up
make docker-compose-down

# Loop through the tests
for (( i=1; i<=$num_tests; i++ ))
do
	make REBUILD=0 docker-compose-up

	# If test fails, try increasing this value
    sleep 20

    output=$(docker compose -f docker-compose-dev.yaml logs | grep consulta | sort | grep -oE "cant_ganadores.{0,3}")
    expected=$(cat <<-END
cant_ganadores: 2
cant_ganadores: 3
cant_ganadores: 3
cant_ganadores: 2
cant_ganadores: 0
END
    )

    if [[ "$output" == "$expected" ]]; then
		echo "Test $i: Success! The output is correct."
		((success_count++))
	else
		echo "Test $i: Error! The output is not correct. It is $output. It should be $expected."
		# Keep relevant information for debugging in case of failure
		docker compose -f docker-compose-dev.yaml logs > "test$i.log"
	fi

    make docker-compose-down
done

echo "Out of $num_tests tests, $success_count succeeded and $((num_tests-success_count)) failed."
