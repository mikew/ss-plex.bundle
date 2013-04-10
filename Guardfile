# A sample Guardfile
# More info at https://github.com/guard/guard#readme

# Add files and commands to this file, like the example:
#   watch(%r{file/path}) { `command(s)` }
#

def python_unittest(test_file)
  root      = Pathname File.expand_path('../', __FILE__)
  test_file = root.join test_file
  dyld_path = [
    '~/Library/Application Support/Plex Media Server/Plug-ins/Framework.bundle/Contents/Resources/Platforms/MacOSX/i386/Frameworks/',
    '~/Library/Application Support/Plex Media Server/Plug-ins/Framework.bundle/Contents/Resources/Versions/2/Platforms/MacOSX/i386/Frameworks/',
    '~/Library/Application Support/Plex Media Server/Plug-ins/Framework.bundle/Contents/Resources/Versions/2/Frameworks/'
  ].join(':').gsub '~/', ENV['HOME'] + '/'
  env = %Q(DYLD_LIBRARY_PATH="#{dyld_path}")

  `[ -f #{test_file} ] && env #{env} python2.5 Contents/Tests/nose_runner.py #{test_file}`
end

guard 'shell' do
  watch(%r{Contents/Code/(.*).py$})       {|m| python_unittest "Contents/Tests/test_#{m[1]}.py" }
  watch(%r{Contents/Tests/test_(.*).py$}) {|m| python_unittest "Contents/Tests/test_#{m[1]}.py" }
end
