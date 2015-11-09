module Jekyll

  class DayProgramPage < Page
    def initialize(site, base, dir, day_id, day)
      @site = site
      @base = base
      @dir = dir
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(base, '_layouts'), 'day_program.html')
      self.data['day'] = day
      self.data['title'] = day['title']
    end
  end

  class DayProgramPageGenerator < Generator
    safe true

    def generate(site)
      if site.layouts.key? 'day_program'
        dir = site.config['day_program_dir'] || 'program'
        prefix = site.config['day_program_prefix'] || 'day'
        existing = []
        site.pages.each do |page|
          if match = page.url.match(%r{^/#{dir}/([^/]+)/[^/]*$})
            existing << match.captures[0]
          end
        end
        site.data['program'].each_with_index do |day, day_index|
          day_id = "#{prefix}#{day_index + 1}"
          if not existing.include? day_id
            site.pages << DayProgramPage.new(site, site.source, File.join(dir, day_id), day_id, day)
          end
        end
      end
    end
  end

end
