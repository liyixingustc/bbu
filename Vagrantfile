# -*- mode: ruby -*-
# vi: set ft=ruby :

# template for django

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # 2 is the latest api version available

  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "bento/centos-7.4"
  config.vm.hostname = 'bbu-web-dev'
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  # create guest OS on host

  config.vm.provision "shell", inline: <<-SHELL
  SHELL
end
