module Jekyll

  class SessionPage < Page
    def initialize(site, base, dir, session_id, session)
      @site = site
      @base = base
      @dir = dir
      @name = 'index.wiki'

      self.process(@name)
      self.read_yaml(File.join(base, '_layouts'), 'session.wiki')
      self.data['title'] = session['title']
    end
  end

  class SessionPageGenerator < Generator
    safe true

    def generate(site)
      if site.layouts.key? 'session'
        dir = site.config['session_dir'] || 'sessions'
        existing = []
        site.pages.each do |page|
          if match = page.url.match(%r{^/#{dir}/([^/]+)/[^/]*$})
            existing << match.captures[0]
          end
        end
        site.data['sessions'].each do |session_id, session|
          if not existing.include? session_id
            site.pages << SessionPage.new(site, site.source, File.join(dir, session_id), session_id, session)
          end
        end
      end
    end
  end

end
