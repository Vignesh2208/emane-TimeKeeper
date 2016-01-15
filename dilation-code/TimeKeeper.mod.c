#include <linux/module.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

MODULE_INFO(vermagic, VERMAGIC_STRING);

__visible struct module __this_module
__attribute__((section(".gnu.linkonce.this_module"))) = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

static const struct modversion_info ____versions[]
__used
__attribute__((section("__versions"))) = {
	{ 0xe58e7fd0, __VMLINUX_SYMBOL_STR(module_layout) },
	{ 0xee1cd666, __VMLINUX_SYMBOL_STR(kmalloc_caches) },
	{ 0x12da5bb2, __VMLINUX_SYMBOL_STR(__kmalloc) },
	{ 0xb2947494, __VMLINUX_SYMBOL_STR(call_usermodehelper_exec) },
	{ 0x68e2f221, __VMLINUX_SYMBOL_STR(_raw_spin_unlock) },
	{ 0xd0d8621b, __VMLINUX_SYMBOL_STR(strlen) },
	{ 0x2d37342e, __VMLINUX_SYMBOL_STR(cpu_online_mask) },
	{ 0x1cefc352, __VMLINUX_SYMBOL_STR(find_vpid) },
	{ 0x81e4d30c, __VMLINUX_SYMBOL_STR(hrtimer_cancel) },
	{ 0xb789fae3, __VMLINUX_SYMBOL_STR(remove_proc_entry) },
	{ 0x5b19634d, __VMLINUX_SYMBOL_STR(div_s64_rem) },
	{ 0xd964b2f3, __VMLINUX_SYMBOL_STR(mutex_unlock) },
	{ 0x54efb5d6, __VMLINUX_SYMBOL_STR(cpu_number) },
	{ 0x91715312, __VMLINUX_SYMBOL_STR(sprintf) },
	{ 0x7bbe7129, __VMLINUX_SYMBOL_STR(kthread_create_on_node) },
	{ 0xe2d5255a, __VMLINUX_SYMBOL_STR(strcmp) },
	{ 0x68dfc59f, __VMLINUX_SYMBOL_STR(__init_waitqueue_head) },
	{ 0x63785b2a, __VMLINUX_SYMBOL_STR(proc_mkdir) },
	{ 0xd87f8a85, __VMLINUX_SYMBOL_STR(current_task) },
	{ 0xc5d325c4, __VMLINUX_SYMBOL_STR(__mutex_init) },
	{ 0x50eedeb8, __VMLINUX_SYMBOL_STR(printk) },
	{ 0xd69b6b07, __VMLINUX_SYMBOL_STR(kthread_stop) },
	{ 0x44b1ea72, __VMLINUX_SYMBOL_STR(netlink_kernel_release) },
	{ 0xb6ed1e53, __VMLINUX_SYMBOL_STR(strncpy) },
	{ 0xb4390f9a, __VMLINUX_SYMBOL_STR(mcount) },
	{ 0x76514cdb, __VMLINUX_SYMBOL_STR(mutex_lock) },
	{ 0x15e89c80, __VMLINUX_SYMBOL_STR(netlink_unicast) },
	{ 0x7b16e129, __VMLINUX_SYMBOL_STR(pid_task) },
	{ 0x1a3d7e49, __VMLINUX_SYMBOL_STR(init_net) },
	{ 0x8ff4079b, __VMLINUX_SYMBOL_STR(pv_irq_ops) },
	{ 0x72f0d84e, __VMLINUX_SYMBOL_STR(__alloc_skb) },
	{ 0xf0fdf6cb, __VMLINUX_SYMBOL_STR(__stack_chk_fail) },
	{ 0x4292364c, __VMLINUX_SYMBOL_STR(schedule) },
	{ 0x86a4889a, __VMLINUX_SYMBOL_STR(kmalloc_order_trace) },
	{ 0xbdb257ba, __VMLINUX_SYMBOL_STR(hrtimer_start) },
	{ 0x12f29f05, __VMLINUX_SYMBOL_STR(pv_cpu_ops) },
	{ 0x57d887d8, __VMLINUX_SYMBOL_STR(wake_up_process) },
	{ 0x1680313d, __VMLINUX_SYMBOL_STR(kmem_cache_alloc_trace) },
	{ 0x67f7403e, __VMLINUX_SYMBOL_STR(_raw_spin_lock) },
	{ 0x56c54284, __VMLINUX_SYMBOL_STR(sched_setscheduler) },
	{ 0xe45f60d8, __VMLINUX_SYMBOL_STR(__wake_up) },
	{ 0xbe2a0dd3, __VMLINUX_SYMBOL_STR(call_usermodehelper_setup) },
	{ 0xb3f7646e, __VMLINUX_SYMBOL_STR(kthread_should_stop) },
	{ 0xa56d356, __VMLINUX_SYMBOL_STR(prepare_to_wait_event) },
	{ 0x5131c3c9, __VMLINUX_SYMBOL_STR(proc_create_data) },
	{ 0x4f68e5c9, __VMLINUX_SYMBOL_STR(do_gettimeofday) },
	{ 0x7972fe64, __VMLINUX_SYMBOL_STR(find_get_pid) },
	{ 0x3b5a1e35, __VMLINUX_SYMBOL_STR(__netlink_kernel_create) },
	{ 0x37a0cba, __VMLINUX_SYMBOL_STR(kfree) },
	{ 0xc4d274bf, __VMLINUX_SYMBOL_STR(send_sig_info) },
	{ 0x781c6eca, __VMLINUX_SYMBOL_STR(hrtimer_init) },
	{ 0x74c134b9, __VMLINUX_SYMBOL_STR(__sw_hweight32) },
	{ 0x75bb675a, __VMLINUX_SYMBOL_STR(finish_wait) },
	{ 0x4f6b400b, __VMLINUX_SYMBOL_STR(_copy_from_user) },
	{ 0x559eac60, __VMLINUX_SYMBOL_STR(__nlmsg_put) },
	{        0, __VMLINUX_SYMBOL_STR(sys_close) },
	{ 0x4cdb3178, __VMLINUX_SYMBOL_STR(ns_to_timeval) },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=";


MODULE_INFO(srcversion, "81C1FD07B578D26A653C307");
