class FavoriteMedicine < ApplicationRecord
  belongs_to :user
  belongs_to :medicine

  validates :medicine_id, uniqueness: { scope: :user_id, message: "is already in favorites" }
end
