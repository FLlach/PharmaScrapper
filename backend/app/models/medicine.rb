class Medicine < ApplicationRecord
  has_many :pharmacy_products
  has_many :favorite_medicines, dependent: :destroy
  has_many :users, through: :favorite_medicines
end
