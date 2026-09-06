class User < ApplicationRecord
  has_secure_password
  has_many :sessions, dependent: :destroy
  has_many :favorite_medicines, dependent: :destroy
  has_many :medicines, through: :favorite_medicines

  normalizes :email_address, with: ->(e) { e.strip.downcase }

  validates :email_address, presence: true
  validates :role, inclusion: { in: %w[standard admin] }

  def admin?
    role == 'admin'
  end
end
