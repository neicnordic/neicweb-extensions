module Jekyll
  module HavingFilter
    def having(input, key, value = nil)
      if value.nil?
        index = input.find_index { |item| item.include?(key) }
      else
        index = input.find_index { |item| item[key] == value }
      end
      index.nil? ? nil : input[index]
    end
  end
end

Liquid::Template.register_filter(Jekyll::HavingFilter)
