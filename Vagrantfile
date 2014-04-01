# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
	config.vm.box = "raylu/debian-testing"
	config.vm.network "forwarded_port", guest: 8888, host: 8888
	config.vm.provision :shell, :path => "vagrant.sh"
	config.vm.provider "virtualbox" do |vb|
		vb.name = "lpmc-site"
	end
end

