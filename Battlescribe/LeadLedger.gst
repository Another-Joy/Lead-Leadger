<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<gameSystem id="my-tactical-game-gst" name="My Tactical Game" revision="1" battleScribeVersion="2.03" xmlns="http://www.battlescribe.net/schema/gameSystemSchema">
  <costTypes>
    <costType id="mp-cost" name="MP" defaultCostLimit="-1.0" hidden="false"/>
    <costType id="mats-cost" name="Mats" defaultCostLimit="-1.0" hidden="false"/>
  </costTypes>
  <profileTypes>
    <profileType id="unit-profile-id" name="Unit">
      <characteristicTypes>
        <characteristicType id="movement" name="M"/>
        <characteristicType id="armor" name="A"/>
        <characteristicType id="control" name="C"/>
        <characteristicType id="health" name="H"/>
      </characteristicTypes>
    </profileType>
    <profileType id="weapon-profile-id" name="Weapons">
      <characteristicTypes>
        <characteristicType id="weapon-range" name="R"/>
        <characteristicType id="weapon-none" name="N"/>
        <characteristicType id="weapon-light" name="L"/>
        <characteristicType id="weapon-medium" name="M"/>
        <characteristicType id="weapon-heavy" name="H"/>
        <characteristicType id="weapon-fortification" name="F"/>
        <characteristicType id="weapon-keywords" name="Keywords"/>
      </characteristicTypes>
    </profileType>
    <profileType id="b88b-b6ca-13c2-bb58" name="Abilities">
      <characteristicTypes>
        <characteristicType id="71a6-c11b-3c40-dde8" name="Description"/>
      </characteristicTypes>
    </profileType>
  </profileTypes>
  <categoryEntries>
    <categoryEntry id="inf" name="Infantry" hidden="false"/>
    <categoryEntry id="veh" name="Vehicle" hidden="false"/>
    <categoryEntry id="apc" name="APC" hidden="false"/>
    <categoryEntry id="b43b-a848-fcd3-f503" name="Light Tank" hidden="false"/>
    <categoryEntry id="201c-1576-d588-aad5" name="IFV" hidden="false"/>
    <categoryEntry id="dc81-ab91-495d-0042" name="MBT" hidden="false"/>
    <categoryEntry id="4972-4598-7035-2b18" name="SPG" hidden="false"/>
    <categoryEntry id="b9a5-fc14-d873-704f" name="Armored Car" hidden="false"/>
  </categoryEntries>
  <forceEntries>
    <forceEntry id="army-list-gst" name="Army List (GST)" hidden="false"/>
  </forceEntries>
  <sharedRules>
    <rule id="5475-29e2-85c2-9a76" name="Assault" hidden="false">
      <description>Can make offensive actions after moving.</description>
    </rule>
    <rule id="8956-be22-469d-2391" name="Transport" hidden="false"/>
  </sharedRules>
  <sharedProfiles>
    <profile id="6851-f823-5b74-bebb" name="NERA Armor" hidden="false" typeId="b88b-b6ca-13c2-bb58" typeName="Abilities">
      <characteristics>
        <characteristic name="Description" typeId="71a6-c11b-3c40-dde8">test description</characteristic>
      </characteristics>
    </profile>
    <profile id="58ec-2f03-cfde-51bd" name="Sloped Armor" hidden="false" typeId="b88b-b6ca-13c2-bb58" typeName="Abilities">
      <characteristics>
        <characteristic name="Description" typeId="71a6-c11b-3c40-dde8">tes 2</characteristic>
      </characteristics>
    </profile>
  </sharedProfiles>
</gameSystem>