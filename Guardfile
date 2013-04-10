def python_unittest(test_file)
  return unless File.exist? test_file

  runner = case RUBY_PLATFORM
  when /linux/  then 'ubuntu'
  when /darwin/ then 'osx'
  end

  system *[ "./run-#{runner}.sh", test_file ]
end

guard 'shell' do
  watch %r{Contents/Code/([^/]+/)*(.*).py$} do |m|
    python_unittest "Contents/Tests/#{m[1]}test_#{m[2]}.py"
  end

  watch %r{Contents/Services/([^/]+/)*(.*).pys?$} do |m|
    python_unittest "Contents/Tests/Services/#{m[1]}test_#{m[2]}.py"
  end

  watch %r{Contents/Tests/([^/]+/)*test_(.*).py$}  do |m|
    python_unittest m[0]
  end

end
