class CreatePharmacyProducts < ActiveRecord::Migration[8.1]
  def change
    create_table :pharmacy_products do |t|
      t.references :pharmacy, null: false, foreign_key: true
      t.references :medicine, null: false, foreign_key: true
      t.string :sku
      t.string :name
      t.string :url
      t.string :image_url

      t.timestamps
    end
  end
end
