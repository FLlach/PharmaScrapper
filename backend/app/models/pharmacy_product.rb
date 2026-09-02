class PharmacyProduct < ApplicationRecord
  belongs_to :pharmacy
  belongs_to :medicine, optional: true
  has_many :price_histories

  alias_attribute :url, :product_url if column_names.include?('product_url')
  alias_attribute :image_url, :image_url if column_names.include?('image_url')
end
