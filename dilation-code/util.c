#include "dilation_module.h"

/***
Contains some basic functions (such as atoi), as well as some TimeKeeper debug functions.
***/

int get_next_value (char *write_buffer);
int atoi(char *s);
struct task_struct* find_task_by_pid(unsigned int nr);
int kill(struct task_struct *killTask, int sig, struct dilation_task_struct* dilation_task);

void print_proc_info(char *write_buffer);

void print_children_info_proc(char *write_buffer);
void print_children_info(struct task_struct *aTask);
void print_children_info_pid(int pid);

int find_children_info(struct task_struct *aTask, int pid);
void print_threads_proc(char *write_buffer);

struct sock *nl_sk = NULL;
struct task_struct *loop_task;

void send_a_message_proc(char * write_buffer);
void send_a_message(int pid);

extern s64 Sim_time_scale;

/*
Wrapper for sending a message to userspace
*/
void send_a_message_proc(char * write_buffer) {
        int pid;
        pid = atoi(write_buffer);
        send_a_message(pid);
}

/*
Send a message from the Kernel to Userspace (to let the process know all LXCs have advanced to a
certain point.
*/
    void send_a_message(int pid) {
    struct nlmsghdr *nlh;
    struct sk_buff *skb_out;
    int msg_size;
    char *msg = "";
    int res;

    msg_size = strlen(msg);

    skb_out = nlmsg_new(msg_size, 0);

    if (!skb_out)
    {

        printk(KERN_ERR "Failed to allocate new skb\n");
        return;

    }
    nlh = nlmsg_put(skb_out, 0, 0, NLMSG_DONE, msg_size, 0);
    NETLINK_CB(skb_out).dst_group = 0;
    strncpy(nlmsg_data(nlh), msg, msg_size);

    res = nlmsg_unicast(nl_sk, skb_out, pid);
    if (res < 0) {
        printk(KERN_INFO "TimeKeeper: Error while sending bak to user %d\n", res);
    }
}

/***
Used when reading the input from a userland process -> the TimeKeeper. Will basically return the next number in a string
***/
int get_next_value (char *write_buffer)
{
        int i;
        for(i = 1; *(write_buffer+i) >= '0' && *(write_buffer+i) <= '9'; i++)
        {
                continue;
        }
        return (i + 1);
}
/***
 Convert string to integer
***/
int atoi(char *s)
{
        int i,n;
        n = 0;
        for(i = 0; *(s+i) >= '0' && *(s+i) <= '9'; i++)
                n = 10*n + *(s+i) - '0';
        return n;
}


/***
Given a pid, returns a pointer to the associated task_struct
***/
struct task_struct* find_task_by_pid(unsigned int nr)
{
        struct task_struct* task;
        rcu_read_lock();
        task=pid_task(find_vpid(nr), PIDTYPE_PID);
        rcu_read_unlock();
        return task;
}


/***
My implementation of the kill system call. Will send a signal to a container. Used for freezing/unfreezing containers
***/
int kill(struct task_struct *killTask, int sig, struct dilation_task_struct* dilation_task) {
        struct siginfo info;
        int returnVal;
        info.si_signo = sig;
        info.si_errno = 0;
        info.si_code = SI_USER;
        if ((returnVal = send_sig_info(sig, &info, killTask)) != 0)
        {
                if (dilation_task != NULL)
                {
                        dilation_task->stopped = -1;
			printk(KERN_INFO "TimeKeeper: Error sending kill msg for pid %d\n", dilation_task->linux_task->pid);
                }
        }
        return returnVal;
}

/*
Wrapper for printing all children of a process - for debugging
*/
void print_children_info_proc(char *write_buffer) {
	int pid;
	struct task_struct* aTask;

	pid = atoi(write_buffer);
	aTask = find_task_by_pid(pid);
	if (aTask != NULL) {
		printk(KERN_INFO "TimeKeeper: Finding children pids for %d\n", aTask->pid);
		print_children_info(aTask);
	}
}

/*
Print all children of a process - for debugging
*/
void print_children_info_pid(int pid) {
        struct task_struct* aTask;

        aTask = find_task_by_pid(pid);
        if (aTask != NULL) {
                printk(KERN_INFO "TimeKeeper: Finding children pids for %d\n", aTask->pid);
                print_children_info(aTask);
        }
}

/*
The recursive function to print all children of a process - for debugging
*/
void print_children_info(struct task_struct *aTask) {
        struct list_head *list;
        struct task_struct *taskRecurse;
        if (aTask == NULL) {
                printk(KERN_INFO "TimeKeeper: Task does not exist\n");
                return;
        }
        if (aTask->pid == 0) {
                return;
        }

        list_for_each(list, &aTask->children)
        {
                taskRecurse = list_entry(list, struct task_struct, sibling);
                if (taskRecurse == NULL || taskRecurse->pid == 0) {
                        return;
                }
		printk("Had child: %d\n",taskRecurse->pid);
                print_children_info(taskRecurse);
        }
}

/***
Given a starting task and pid, searches all children of that task, looking for a matching PID. If we return 1,
	then there exists a child in this container with that pid, else -1
***/
int find_children_info(struct task_struct *aTask, int pid) {
        struct list_head *list;
        struct task_struct *taskRecurse;
        if (aTask == NULL) {
                printk(KERN_INFO "TimeKeeper: Task does not exist\n");
                return -1;
        }
        if (pid == aTask->pid) {
                printk(KERN_INFO "TimeKeeper: Task exists for this pid : %d in the experiment \n", pid);
                return 1;
        }

        if (aTask->pid == 0) {
                return -1;
        }

        list_for_each(list, &aTask->children)
        {
                taskRecurse = list_entry(list, struct task_struct, sibling);
                if (taskRecurse == NULL) {
                        return -1;
                }
		if (taskRecurse->pid == 0) {
			return -1;
		}
    //            printk("Had child: %d\n",taskRecurse->pid);
               if (find_children_info(taskRecurse, pid) == 1) {
			return 1;
		}
        }
	return -1;
}


/***
Comapres 2 task_structs, outputs things such as the TDF, virt_start_time and so forth
***/
void print_proc_info(char *write_buffer) {
        int pid,pid2, value;
        struct task_struct* aTask;
        struct task_struct* aTask2;
        s64 now;
        s32 rem;
        struct timeval now_timeval;
        s64 tempTime;
        struct timeval ktv, ktv2;
        s64 real_running_time;
        s64 dilated_running_time;

        pid = atoi(write_buffer);
        aTask = find_task_by_pid(pid);
        value = get_next_value(write_buffer);
        pid2 = atoi(write_buffer + value);
        aTask2 = find_task_by_pid(pid2);

        if (aTask != NULL && aTask2 != NULL) {
        	do_gettimeofday(&now_timeval);
        	now = timeval_to_ns(&now_timeval);
        	printk(KERN_INFO "TimeKeeper: ---------------STARTING COMPARE--------------\n");
                real_running_time = now - aTask->virt_start_time;
                if (aTask->dilation_factor > 0) {
			dilated_running_time = div_s64_rem( (real_running_time - aTask->past_physical_time)*1000 ,aTask->dilation_factor,&rem) + aTask->past_virtual_time;
                        tempTime = dilated_running_time + aTask->virt_start_time;
                }
                else {
                        dilated_running_time = (real_running_time - aTask->past_physical_time) + aTask->past_virtual_time;
                        tempTime = dilated_running_time + aTask->virt_start_time;
                }
                printk(KERN_INFO "TimeKeeper: now: %lld d_r_t: %lld time: %lld\n", now, dilated_running_time, tempTime);
                ktv = ns_to_timeval(tempTime);
                real_running_time = now - aTask2->virt_start_time;
                if (aTask2->dilation_factor > 0) {
			dilated_running_time = div_s64_rem( (real_running_time - aTask2->past_physical_time)*1000 ,aTask2->dilation_factor,&rem) + aTask2->past_virtual_time;
                        tempTime = dilated_running_time + aTask2->virt_start_time;
                }
                else {
                        dilated_running_time = (real_running_time - aTask2->past_physical_time) + aTask2->past_virtual_time;
                        tempTime = dilated_running_time + aTask2->virt_start_time;
                }
                ktv2 = ns_to_timeval(tempTime);
        	printk(KERN_INFO "TimeKeeper: PID: %d %d TGID: %d %d\n", aTask->pid, aTask2->pid, aTask->tgid, aTask2->tgid);
	        printk(KERN_INFO "TimeKeeper: Dilation %d %d\n", aTask->dilation_factor, aTask2->dilation_factor);
        	printk(KERN_INFO "TimeKeeper: virt_start_time %lld %lld\n", aTask->virt_start_time, aTask2->virt_start_time);
	        printk(KERN_INFO "TimeKeeper: diff %lld %lld\n", now - aTask->virt_start_time, now - aTask2->virt_start_time);
        	printk(KERN_INFO "TimeKeeper: current seconds %ld %ld\n", ktv.tv_sec, ktv2.tv_sec);
	        printk(KERN_INFO "TimeKeeper: freeze_time %lld %lld\n", aTask->freeze_time, aTask2->freeze_time);
        	printk(KERN_INFO "TimeKeeper: past_physical_time %lld %lld\n", aTask->past_physical_time, aTask2->past_physical_time);
	        printk(KERN_INFO "TimeKeeper: past_virtual_time %lld %lld\n", aTask->past_virtual_time, aTask2->past_virtual_time);
        }

        else {
                printk(KERN_INFO "TimeKeeper: A task is null\n");
        }
        return;
}

/*
Prints all threads of a process - for debugging
*/
void print_threads_proc(char *write_buffer) {
	struct task_struct *me;
	struct task_struct *t;
	int pid;
	pid = atoi(write_buffer);
	me = find_task_by_pid(pid);
	t = me;
	printk(KERN_INFO "TimeKeeper: Finding threads for pid: %d\n", me->pid);
	do {
    		printk(KERN_INFO "TimeKeeper: Pid: %d %d\n",t->pid, t->tgid);
	} while_each_thread(me, t);
	return;
	}


/* Add to tail of schedule queue */
int add_to_schedule_list(struct dilation_task_struct * lxc, struct task_struct *new_task, s64 FREEZE_QUANTUM, s64 highest_dilation){


	int linux_time_quanta = 0;
	int lowest_linux_time_quanta = 100; // 5 ms
	int dilation_factor;

	int dil;
        s64 temp_proc;
        s64 temp_high;
        s32 rem;
	struct task_struct *me;
        struct task_struct *t;
	s64 window_duration;
	s64 expected_increase;
	int n_threads = 0;
	s64 base_time_quanta;



	if(new_task == NULL || lxc == NULL)
		return -1;

	if(hmap_get(&lxc->valid_children, &new_task->pid) != NULL) // child already exists. don't add
		return 0;


	lxc_schedule_elem * new_element = (lxc_schedule_elem *)kmalloc(sizeof(lxc_schedule_elem), GFP_KERNEL);
	if(new_element == NULL)
		return -1;


	new_element->static_priority = new_task->static_prio;


	/** TODO Handle lower priority processes **/

	if(new_element->static_priority  < 120)
		linux_time_quanta = 20*(140 - new_element->static_priority); // in ms
	else{

		linux_time_quanta = 5*(20); // 100 ms for now
	}
	
	

        // temp_proc and temp_high are temporary dilations for the container and leader respectively.
        // this is done just to make sure the Math works (no divide by 0 errors if the TDF is 0, by making the temp TDF 1)
        temp_proc = 0;
        temp_high = 0;

        if (highest_dilation == 0)
                temp_high = 1;
        else if (highest_dilation < 0)
                temp_high = highest_dilation*-1;

        dil = new_task->dilation_factor;

        if (dil == 0)
                temp_proc = 1;
        else if (dil < 0)
                temp_proc = dil*-1;


	me = new_task;
	t = me;
	n_threads = 0;
	do {
		n_threads++;
	} while_each_thread(me, t);



	if(dil == 0){
		base_time_quanta = 1*Sim_time_scale;
	}
	else{
		base_time_quanta = div_s64_rem(new_task->dilation_factor,1000,&rem)*Sim_time_scale;
	}

	
	if(new_element->static_priority  < 120){

		linux_time_quanta = 20*(140 - new_element->static_priority); // in ms
		base_time_quanta = base_time_quanta*(140 - new_element->static_priority)* 200000; // 200000 = 1000000/5
		lxc->rr_run_time += (int)(140 - new_element->static_priority)/5;
	}
	else{

		linux_time_quanta = 5*(20); // 100 ms for now
		base_time_quanta = base_time_quanta*1000000;
		lxc->rr_run_time += 1;
	}
	

	printk(KERN_INFO "TimeKeeper : PID : %d, Base Quanta : %lld. N_threads : %d. expected_increase : %lld\n", new_task->pid, base_time_quanta, n_threads, expected_increase);

	new_element->share_factor = base_time_quanta;
	new_element->curr_task = new_task;
	new_element->pid = new_task->pid;
	new_element->duration_left = base_time_quanta;

	llist_append(&lxc->schedule_queue, new_element); // append to tail of schedule queue.
	hmap_put(&lxc->valid_children, &new_element->pid, new_element);
	
	return 0;


}

/* Remove head of schedule queue and return the task_struct of the head element */
struct task_struct * pop_schedule_list(struct dilation_task_struct * lxc){

	if(lxc == NULL)
		return NULL;

	lxc_schedule_elem * head;
	head = llist_pop(&lxc->schedule_queue);
	struct task_struct * curr_task;

	if(head != NULL){
		curr_task = head->curr_task;
		hmap_remove(&lxc->valid_children, &head->pid);
		kfree(head);
		return curr_task;
	}


	return NULL;

}

/* Get pointer to task_Struct of head but don't remove the element from the schedule list */
lxc_schedule_elem * schedule_list_get_head(struct dilation_task_struct * lxc){

	if(lxc == NULL)
		return NULL;


	return llist_get(&lxc->schedule_queue, 0);


}




/* requeue schedule queue, i.e pop from head and add to tail */
void requeue_schedule_list(struct dilation_task_struct * lxc){

	if(lxc == NULL)
		return;

	lxc_schedule_elem * head;
	head = llist_pop(&lxc->schedule_queue);
	if(head != NULL){
		llist_append(&lxc->schedule_queue, head);
		hmap_put(&lxc->valid_children, &head->pid, head);
	}

}

void clean_up_schedule_list(struct dilation_task_struct * lxc){

	struct task_struct * curr_task = pop_schedule_list(lxc);
	while(curr_task != NULL){
		curr_task = pop_schedule_list(lxc);
	}

	hmap_destroy(&lxc->valid_children);
	llist_destroy(&lxc->schedule_queue);	

}

int schedule_list_size(struct dilation_task_struct * lxc){

	if(lxc == NULL)
		return 0;
	
	return llist_size(&lxc->schedule_queue);

}
