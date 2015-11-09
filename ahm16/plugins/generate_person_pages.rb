module Jekyll

  class PersonPage < Page
    def initialize(site, base, dir, person_id, person)
      @site = site
      @base = base
      @dir = dir
      @name = 'index.wiki'

      self.process(@name)
      self.read_yaml(File.join(base, '_layouts'), 'person.wiki')
      self.data['title'] = person['name']
    end
  end

  class PersonPageGenerator < Generator
    safe true

    def generate(site)
      if site.layouts.key? 'person'
        dir = site.config['people_dir'] || 'people'
        existing = []
        site.pages.each do |page|
          if match = page.url.match(%r{^/#{dir}/([^/]+)/[^/]*$})
            existing << match.captures[0]
          end
        end
        site.data['people'].each do |person_id, person|
          if not existing.include? person_id
            site.pages << PersonPage.new(site, site.source, File.join(dir, person_id), person_id, person)
          end
        end
      end
    end
  end

end
