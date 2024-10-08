Name:           cargo-packaging
Version:        1.2.0
Release:        1
Summary:        Macros and tools to assist with cargo and rust packaging
License:        MPL-2.0
Group:          Development/Languages/Rust
URL:            https://github.com/Firstyear/cargo-packaging
Source0:        %{name}-%{version}.tar.xz
Source1:        vendor.tar.zst
Source2:        config.toml
Requires:       cargo-auditable
Requires:       rust
Requires:       cargo
Requires:       zstd

BuildRequires:  rust
BuildRequires:  cargo
BuildRequires:  zstd

Conflicts:      rust-packaging

%description
A set of macros and tools to assist with cargo and rust packaging.

%prep
%autosetup -a1 -n %{name}-%{version}/%{name}
install -D -m 644 %{SOURCE2} .cargo/config.toml

%build
%ifarch %arm32
%global sb2_target armv7-unknown-linux-gnueabihf
%endif
%ifarch %arm64
%global sb2_target aarch64-unknown-linux-gnu
%endif
%ifarch %ix86
%global sb2_target i686-unknown-linux-gnu
%endif

# When cross-compiling under SB2 rust needs to know what arch to emit
# when nothing is specified on the command line. That usually defaults
# to "whatever rust was built as" but in SB2 rust is accelerated and
# would produce x86 so this is how it knows differently. Not needed
# for native x86 builds
export SB2_RUST_TARGET_TRIPLE=%{sb2_target}
export RUST_HOST_TARGET=%{sb2_target}
export RUST_TARGET=%{sb2_target}
export TARGET=%{sb2_target}
export HOST=%{sb2_target}

%ifarch %arm32 %arm64
# This should be define...
export CROSS_COMPILE=%{sb2_target}

# This avoids a malloc hang in sb2 gated calls to execvp/dup2/chdir
# during fork/exec. It has no effect outside sb2 so doesn't hurt
# native builds.
export SB2_RUST_EXECVP_SHIM="/usr/bin/env LD_PRELOAD=/usr/lib/libsb2/libsb2.so.1 /usr/bin/env"
export SB2_RUST_USE_REAL_EXECVP=Yes
export SB2_RUST_USE_REAL_FN=Yes
%endif

cargo build --offline --release --jobs 1 --target %{sb2_target} --verbose

%install
install -D -p -m 0644 -t %{buildroot}%{_fileattrsdir} rust.attr
install -D -p -m 0644 -t %{buildroot}%{_rpmconfigdir}/macros.d macros.cargo
install -D -p -m 0755 -t %{buildroot}%{_rpmconfigdir} target/%{sb2_target}/release/rust-rpm-prov
install -D -p -m 0755 -t %{buildroot}%{_sysconfdir}/zsh_completion.d target/%{sb2_target}/release/build/completions/_rust-rpm-prov
install -D -p -m 0755 -t %{buildroot}%{_sysconfdir}/bash_completion.d target/%{sb2_target}/release/build/completions/rust-rpm-prov.bash

%files
%{_fileattrsdir}/rust.attr
%{_rpmconfigdir}/macros.d/macros.cargo
%{_rpmconfigdir}/rust-rpm-prov

%dir %{_sysconfdir}/zsh_completion.d
%dir %{_sysconfdir}/bash_completion.d
%{_sysconfdir}/zsh_completion.d/*
%{_sysconfdir}/bash_completion.d/*
