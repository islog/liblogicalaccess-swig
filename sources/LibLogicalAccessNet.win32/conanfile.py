from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os

class LLASwig(ConanFile):
    name = "LogicalAccessSwig"
    version = "2.2.0"
    license = "<Put the package license here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of LLA here>"
    settings = "os", "compiler", "build_type", "arch"
    default_options = 'LogicalAccess:LLA_BUILD_PKCS=True','LogicalAccess:LLA_BUILD_IKS=True', 'LogicalAccess:LLA_BUILD_UNITTEST=True', \
                        'LogicalAccessPrivate:LLA_BUILD_UNITTEST=True'
    generators = "cmake"
    revision_mode = "scm"

    def requirements(self):
        try:
            self.requires('LogicalAccessPrivate/' + self.version + '@islog/' + self.channel)
            self.requires('LogicalAccessNFC/' + self.version + '@islog/' + self.channel)
        except ConanException:
            self.requires('LogicalAccessPrivate/' + self.version + '@islog/' + tools.Git().get_branch())
            self.requires('LogicalAccessNFC/' + self.version + '@islog/' + tools.Git().get_branch())

    
    def configure(self):
        if self.settings.os == 'Windows':
            self.options['LogicalAccess'].LLA_BUILD_RFIDEAS = True
    
    def configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        cmake = self.configure_cmake()
        cmake.install()

    def imports(self):
        self.copy("*.so*", "lib", "lib")
	
    def package_info(self):
        pass
