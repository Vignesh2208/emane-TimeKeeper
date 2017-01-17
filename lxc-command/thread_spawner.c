
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#define N_THREADS 10

typedef struct thread_arg_struct {

	int thread_no;
} thread_arg;

void * threadFn( void * ptr) {

	thread_arg * arg = ptr;
	int i = 0;

	for(i = 0; i < 100; i ++){
		int j = 0;
		printf("Thread %d: Count = %d\n", arg->thread_no,i);
		for(j = 0; j < 10000000; j++);
	}
		
}

thread_arg args[N_THREADS];

int main(){

	pthread_t tid[N_THREADS];
	int i = 0;
	for(i = 0; i < N_THREADS; i++) {
		args[i].thread_no = i + 1;
		pthread_create(&tid[i],NULL,threadFn,&args[i]);
	}

	for(i = 0; i < N_THREADS; i++) {
		pthread_join(tid[i],NULL);

	}
	return 0;
}
