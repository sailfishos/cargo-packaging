Name:           cargo-packaging
Version:        1.2.0
Release:        1
Summary:        Macros and tools to assist with cargo and rust packaging
License:        MPL-2.0
Group:          Development/Languages/Rust
URL:            https://github.com/Firstyear/cargo-packaging
Source0:        %{name}-%{version}.tar.xz
Source1:        vendor.tar.xz
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

%define BUILD_DIR ../build

%prep

# RUST START
mkdir -p "%BUILD_DIR"
rm -f "%BUILD_DIR"/.env

%ifarch %arm32
%define SB2_TARGET armv7-unknown-linux-gnueabihf
%endif
%ifarch %arm64
%define SB2_TARGET aarch64-unknown-linux-gnu
%endif
%ifarch %ix86
%define SB2_TARGET i686-unknown-linux-gnu
%endif

# When cross-compiling under SB2 rust needs to know what arch to emit
# when nothing is specified on the command line. That usually defaults
# to "whatever rust was built as" but in SB2 rust is accelerated and
# would produce x86 so this is how it knows differently. Not needed
# for native x86 builds
{
  echo "export SB2_RUST_TARGET_TRIPLE=%SB2_TARGET"
  echo "export RUST_HOST_TARGET=%SB2_TARGET"

  echo "export RUST_TARGET=%SB2_TARGET"
  echo "export TARGET=%SB2_TARGET"
  echo "export HOST=%SB2_TARGET"
  echo "export SB2_TARGET=%SB2_TARGET"
  echo "export CARGO_HOME=%BUILD_DIR/cargo"
}  >> "%BUILD_DIR"/.env

%ifarch %arm32 %arm64
# This should be define...
echo "export CROSS_COMPILE=%SB2_TARGET" >> "%BUILD_DIR"/.env

# This avoids a malloc hang in sb2 gated calls to execvp/dup2/chdir
# during fork/exec. It has no effect outside sb2 so doesn't hurt
# native builds.
echo "export SB2_RUST_EXECVP_SHIM=\"/usr/bin/env LD_PRELOAD=/usr/lib/libsb2/libsb2.so.1 /usr/bin/env\"" >> "%BUILD_DIR"/.env
echo "export SB2_RUST_USE_REAL_EXECVP=Yes" >> "%BUILD_DIR"/.env
echo "export SB2_RUST_USE_REAL_FN=Yes" >> "%BUILD_DIR"/.env
%endif
# RUST END

%autosetup -a1

%build
source "%BUILD_DIR"/.env

cargo build --offline --release --manifest-path %{name}/Cargo.toml --jobs 1

%install
install -D -p -m 0644 -t %{buildroot}%{_fileattrsdir} %{_builddir}/%{name}/rust.attr
install -D -p -m 0644 -t %{buildroot}%{_rpmconfigdir}/macros.d %{_builddir}/%{name}/macros.cargo

install -D -p -m 0755 -t %{buildroot}%{_rpmconfigdir} %{_builddir}/%{name}/target/${SB2_TARGET}/release/rust-rpm-prov

install -D -p -m 0755 -t %{buildroot}%{_sysconfdir}/zsh_completion.d %{_builddir}/%{name}/target/${SB2_TARGET}/release/build/completions/_rust-rpm-prov
install -D -p -m 0755 -t %{buildroot}%{_sysconfdir}/bash_completion.d %{_builddir}/%{name}/target/${SB2_TARGET}/release/build/completions/rust-rpm-prov.bash

%files

%{_fileattrsdir}/rust.attr
%{_rpmconfigdir}/macros.d/macros.cargo
%{_rpmconfigdir}/rust-rpm-prov

%dir %{_sysconfdir}/zsh_completion.d
%dir %{_sysconfdir}/bash_completion.d
%{_sysconfdir}/zsh_completion.d/*
%{_sysconfdir}/bash_completion.d/*
