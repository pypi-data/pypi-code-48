import setuptools

with open("README.md","r") as fh:
	long_description =fh.read();
	
setuptools.setup(
	name="qpautomator",
	version="0.0.2",
	autor="mrsha",
	autor_email="mrsha1195@163.com",
	description="automator on qpython3L",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/xxx",
	package=setuptools.find_packages(),
	calssifiers=[
		"Programming Language::Python::3",
		"License::OSI Approved::MIT License",
		"Operating System::OS Independent",
	],
)
