# Translating Uploader.json to Core Specs
In order to ease the transition from classic collection to core, an investigation was done to see if we can maintain compatibility with currently existing remove.conf files. Results follow.

## Part 1: Comparing Symbolic Names
In January 2019 it became possible to specify commands/files to remove using the "symbolic name" from the uploader.json. Since these names are derived from core components themselves, it stands to reason that a 1:1 relationship can be established.

Indeed, the majority of symbolic names were able to be mapped to components. Here are the few that were not, however there are workable solutions:

### Commands
- `getconf_pagesize` - **Renamed**. In core, this spec is named `getconf_page_size`
- `lspci_kernel` - **Duplicate**. This is an alias of the `lspci` spec
- `netstat__agn`  - **Renamed**. In core, this spec is named `netstat_agn`
- `rpm__V_packages` - **Renamed**. In core, this spec is named `rpm_V_packages`
- `ss_tupna` - **Duplicate**. This is an alias of the `ss` spec
- `systemd_analyze_blame` - **Absent**. This spec is not available in core, even under a different name. I can only assume we no longer collect it.

### Files
- `machine_id1` - **Aggregated**. Part of the `machine_id` spec. (no one should be blacklisting this anyway)
- `machine_id2` - **Aggregated**. Part of the `machine_id` spec. (no one should be blacklisting this anyway)
- `machine_id3` - **Aggregated**. Part of the `machine_id` spec. (no one should be blacklisting this anyway)
- `grub2_efi_grubenv` - **Absent**. This spec is not available in core, even under a different name. I can only assume we no longer collect it.
- `grub2_grubenv` - **Absent**. This spec is not available in core, even under a different name. I can only assume we no longer collect it.
- `limits_d` - **Aggregated**. Part of the `limits_conf` spec
- `modprobe_conf` - **Aggregated**. Part of the `modprobe` spec
- `modprobe_d` - **Aggregated**. Part of the `modprobe` spec
- `ps_auxwww` - **Aggregated**. Part of the `ps_aux`, `psauxcww`, and `ps_auxww` specs under `SosSpecs`
- `rh_mongodb26_conf` - **Aggregated**. Part of the `mongod_conf` spec
- `sysconfig_rh_mongodb26` - **Aggregated**. Part of the `sysconfig_mongod` spec
- `redhat_access_proactive_log` - **Absent**. This spec is not available in core, even under a different name. I can only assume we no longer collect it.

### Globs
- `krb5_conf_d` - **Aggregated**. Part of the `krb5` spec.

Based on these findings, there are 4 specs in uploader.json that are no longer applicable in core -- `systemd_analyze_blame`, `grub2_efi_grubenv`, `grub2_grubenv`, `redhat_access_proactive_log` -- which is OK from a remove.conf standpoint, since we wouldn't collect them in the first place. We therefore have **100% coverage on symbolic names for remove.conf**, provided we do the appropriate mapping for renamed and aggregated specs.

## Part 2: Comparing Raw Commands & Files
Because symbolic name lookup was added only a year and a half ago, it may be more likely that existing remove.conf configurations are using the raw commands and files as defined in uploader.json. Thus we need a way to map those commands and files back to specs -- the problem being that they don't always match up exactly, and core specs use macro substitution based on `ps aux` or other such dependencies. 

Results were found by matching specs from uploader.json and core based on symbolic names, then comparing the commands associated with them. Investigation results follow.

**It's important to note that insights-core compiles a Python regular expression from commands and files defined in the blacklist, so any commands and globs with wildcard matching in uploader.json may not work as expected.**

### Commands
#### Unusable specs in legacy remove.conf
The old remove.conf was comma separated, so the following specs would not be usuable based on the raw command, since the commands contain commas:
- `installed_rpms`
- `lsblk_pairs`
- `lvs_noheadings`
- `pvs_noheadings`

Based on this, it's probable that **these specs are of low importance for compatibility**.

#### Specs containing regex tokens
These commands contain `*` wildcards or other regex tokens, which would break the command match after being complied into a regex in the core blacklist:
- `certificates_enddate`
- `dig_dnssec`
- `dig_edns`
- `dig_noedns`
- `findmnt_lo_propagation`
- `hammer_task_list`
- `libkeyutils`
- `libkeyutils_objdumps`
- `max_uid`
- `multicast_querier`
- `numeric_user_group_name`
- `satellite_mongodb_storage_engine`
- `sealert`
- `subscription_manager_installed_product_ids`
- `systemctl_show_all_services`
- `systemctl_show_target`
- `tomcat_vdc_fallback`
- `woopsie`

Based on this, **we cannot match these raw commands to core specs**.

#### Specs with `%s` macros in core that match after their prequisites are met
There are some specs in core that use prequisite functions to determine certain information. In many cases, the `%s` substitution will result in specs that match uploader.json:
- `httpd_V`
- `httpd_M`
- `md5chk_files`
- `modinfo_all`

Based on this, we can assume **these specs are OK to specify with the raw commands.**

#### Specs that do not match
These specs have similar commands, but they are too different (e.g. dropping `/bin` or `/usr/bin` from the command path) to form a match based on the current filter implementation:
- `ls_etc`
- `ps_eo`
- `uname`
- `vgdisplay`

Based on this, **we cannot match these raw commands to core specs**.

### Files
#### Specs that match after filter regex compilation
These specs contain regex tokens in uploader.json. After being compiled, they match paths in insights-core.
- `imagemagick_policy` - uploader.json has versons for /usr/lib and /usr/lib64, core has glob starting with /usr/lib*
- `pluginconf_d`
- `yum_repos_d` - the uploader.json version of `yum_repos_d` will only match against `*.repo` files

Based on this, we can assume **these specs are OK to specify with the raw file paths.**

#### Specs with `%s` macros in core that match after their prequisites are met
There are some specs in core that use prequisite functions to determine certain information. In many cases, the `%s` substitution will result in specs that match uploader.json:
- `catalina_out` - uploader.json has multiple versions of the spec for different dirs, core has dynamic directory to be filled in

Based on this, we can assume **these specs are OK to specify with the raw file paths.**

#### Specs that do not match 100%
These specs have at least one matching path, and at least one non-matching path between uploader.json and insights-core.
- `sysconfig_memcached` - `/etc/sysconfig/memcached` is accounted for in core, but `/var/lib/config-data/memcached/etc/sysconfig/memcached` is replaced with `/var/lib/config-data/puppet-generated/memcached/etc/sysconfig/memcached`

Based on this, **we cannot _always_ match these raw file paths to core specs**.

#### Specs after file expansion
There is one more condition not explicit to uploader.json. In the classic insights-client collection, it is possible to skip files not explicitly defined in uploader.json, which are checked after path expansion is done upon regex-composed filepaths. E.g., one can specify a specific file in `/etc/yum.repos.d/` to omit, as long as it appears in the results of the file spec parsing (i.e., all `*.repo` files in that directory). Core checks the blacklist filters for every command and file it collects, so any arbitrarily specified file should be accounted for during collection.


### Globs
#### Unusable specs in legacy remove.conf
List of glob specs in uploader.json that cannot be applied with their raw glob paths:
- `cpu_cores`
- `cpu_siblings`
- `mac_addresses`
- `httpd_conf`
- `httpd_conf_scl_httpd24`
- `httpd_conf_scl_jbcs_httpd24`
- `bond_dynamic_lb`
- `boot_loader_entries`
- `amq_broker`
- `nginx_conf`
- `kubepods_cpu_quota`
- `libvirtd_qemu_log`
- `mlx4_port`
- `mysql_log`
- `numa_cpus`
- `scsi_fwver`
- `scsi_eh_deadline`

Because of the nature of how glob specs are defined, with the current core blacklist implementation, no glob specs can be translated by their raw paths, as the wildcard tokens would break the regex matching.

The Insights client's classic collection treats glob specs as files after parsing, so the remove.conf `files` section is applied post-glob parse. It is not a valid path to specify a glob's raw file path or symbolic name in the current remove.conf implementation. **However, arbitrary file paths are allowed**, since all paths parsed from the glob specs will be checked against remove.conf.

Based on this, it's probable that **these specs are of low importance for compatibility**.

## Part 3: Conclusion

So, our ability to leverage possible existing "classic" remove.conf configs in core boils down to this.

What we know:
- We have 100% coverage for symbolic names (with a little bit of massaging for a few) because they are mostly derived from core specs already
- We have partial coverage on raw commands
- We have very close to 100% coverage on raw filenames
- We have 0% coverage on raw glob specs (this is unchanged from classic)
- We have the ability to omit arbitrary files
	- In classic: provided they match a path expansion from glob or file
	- In core: I believe any file at all can be omitted if specified in the blacklist (correct me if I'm wrong here)

Based on the findings, I think an ideal implementation would be something like the following:

1. If a symbolic name is provided, match the symbolic name to a core spec
2. If a raw command or file is provided, try to reverse-lookup the symbolic name using uploader.json (or defined mapping file), then match it to a core spec
3. If something yet undeterminable is provided, try to pass it through to core as-is
	- If it's an arbitrary command
		- Classically, the provided commands _must_ match what's in uploader.json. If nothing matches, it's a noop.
	- If it's an arbitrary file
		- In the classic data collector, we provided the ability to match files after path expansion, so if something like this is provided (e.g. a specific file in `yum.repos.d`), it should be skipped. Insights-core ought to automatically skip it based on the `FileProvider` implementation.

## Appendix
### Classic Insights Collection Flow with Remove.conf

1. Loop through uploader.json command specs
	1. If symbolic name or raw command matches anything in remove.conf, skip it
	2. Parse the command spec against any relevant pre-commands*
	3. Loop through the pre-command parsed commands
		1. If the command matches anything in remove.conf, skip it
		2. Otherwise, run the command and archive the output

	* The only pre-command we use in classic collection is `iface`, which is used to generate arguments for ethtool commands.

2. Loop through uploader.json file specs
	1. If symbolic name or raw file matches anything in remove.conf, skip it
	2. Parse the file spec by doing a directory listing and creating a list of files that regex-match the file spec
	3. Loop through the generated file list
		1. If the file matches anything in remove.conf, skip it
		2. Otherwise, archive the file contents

3. Loop through glob file specs
	1. Parse glob spec into paths
	2. Loop through list of paths
		1. If path matches anything in remove.conf files, skip it
		2. Otherwise, archive the file contents