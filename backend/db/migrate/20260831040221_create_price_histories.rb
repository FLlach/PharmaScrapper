class CreatePriceHistories < ActiveRecord::Migration[8.1]
  def change
    create_table :price_histories do |t|
      t.references :pharmacy_product, null: false, foreign_key: true
      t.integer :price_regular
      t.integer :price_offer
      t.boolean :in_stock
      t.datetime :captured_at

      t.timestamps
    end
  end
end
