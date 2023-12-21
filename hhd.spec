Name:           hhd
Version:        {{{ git_dir_version }}}
Release:        1%{?dist}
Summary:        Handheld Daemon is a project that aims to provide utilities for managing handheld devices

License:        MIT
URL:            https://github.com/KyleGospo/hhd
VCS:            {{{ git_dir_vcs }}}
Source:        	{{{ git_dir_pack }}}     

BuildArch:      noarch
BuildRequires:  systemd-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  python3-build
BuildRequires:  python3-installer
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel

Requires:       python3
Requires:       python3-evdev
Requires:       python3-rich
Requires:       python3-yaml

%description
Handheld Daemon is a project that aims to provide utilities for managing handheld devices. With features ranging from TDP controls, to controller remappings, and gamescope session management. This is done through a plugin system, and a dbus daemon, which will expose the settings of the plugins in a UI agnostic way.

%prep
{{{ git_dir_setup_macro }}}

%build
python3 -m build --wheel --no-isolation

%install
python3 -m installer --destdir="%{buildroot}" dist/*.whl
mkdir -p %{buildroot}%{_udevrulesdir}
install -m644 usr/lib/udev/rules.d/83-hhd.rules %{buildroot}%{_udevrulesdir}/83-hhd.rules
mkdir -p %{buildroot}%{_unitdir}
install -m644 usr/lib/systemd/system/hhd@.service %{buildroot}%{_unitdir}/hhd@.service

%files
%doc readme.md
%license LICENSE
%{_bindir}/hhd*
%{python3_sitelib}/hhd*
%{_udevrulesdir}/83-hhd.rules
%{_unitdir}/hhd@.service

%changelog
{{{ git_dir_changelog }}}
