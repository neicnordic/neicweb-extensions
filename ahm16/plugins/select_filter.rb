module Jekyll
  module SelectFilter
    def select(input, key, value = nil)
      if input.is_a?(Hash)
        if value.nil?
          return input.select { |k, h| h.include?(key) }
        else
          return input.select { |k, h| h[key] == value }
        end
      end
      if value.nil?
        return input.select { |h| h.include?(key) }
      else
        return input.select { |h| h[key] == value }
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::SelectFilter)
