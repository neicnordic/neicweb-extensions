module Jekyll

  class TalkPage < Page
    def initialize(site, base, dir, talk_spec, talk)
      @site = site
      @base = base
      @dir = dir
      @name = 'index.wiki'

      self.process(@name)
      self.read_yaml(File.join(base, '_layouts'), 'talk.wiki')
      self.data['title'] = talk['title']
    end
  end

  class TalkPageGenerator < Generator
    safe true

    def generate(site)
      if site.layouts.key? 'session'
        dir = site.config['session_dir'] || 'sessions'
        existing = []
        site.pages.each do |page|
          if match = page.url.match(%r{^/#{dir}/([^/]+/[^/]+)/[^/]*$})
            existing << match.captures[0]
          end
        end
        site.data['sessions'].each do |session_id, session|
          (session['talks']||[]).each do |talk|
            talk_spec = session_id + '/' + (talk['id'] || talk['speaker'])
            if not existing.include? talk_spec
              site.pages << TalkPage.new(site, site.source, File.join(dir, talk_spec), talk_spec, talk)
            end
          end
        end
      end
    end
  end

end
